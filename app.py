# =====================================================
# AUTO EDA AGENT — PHASES 1 TO 5 (FULL PIPELINE)
# =====================================================

# ============================
# Imports
# ============================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai


plt.rcParams["figure.figsize"] = (5, 2.5)
plt.rcParams["axes.titlesize"] = 10
plt.rcParams["axes.labelsize"] = 9

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Auto EDA Agent",
    page_icon="📊",
    layout="wide"
)


# ============================
# Gemini Configuration
# ============================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


# =====================================================
# PHASE 3 — REASONING (PLAN GENERATION)
# =====================================================
def generate_eda_plan(user_goal: str, df: pd.DataFrame) -> str:
    prompt = f"""
You are a senior data analyst.

User goal:
{user_goal}

Dataset details:
- Columns: {list(df.columns)}
- Data types: {df.dtypes.to_dict()}
- Rows: {df.shape[0]}

Your task:
- Create a clear step-by-step EDA plan
- Do NOT write code
- Do NOT generate insights
- Only list analysis steps
"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


# =====================================================
# PHASE 4 — TOOL FUNCTIONS (EXECUTION LAYER)
# =====================================================
def analyze_structure(df):
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.to_dict()
    }


def analyze_missing_values(df):
    return df.isnull().sum().to_dict()


def analyze_statistics(df):
    return df.describe(include="all").to_dict()


def plot_numeric_distributions(df, max_charts=5):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if len(numeric_cols) == 0:
        return

    # PRIORITIZATION LOGIC
    priority_cols = []

    # 1️⃣ Target variable first (if exists)
    if "Survived" in numeric_cols:
        priority_cols.append("Survived")

    # 2️⃣ High-variance features
    variance = df[numeric_cols].var().sort_values(ascending=False)
    for col in variance.index:
        if col not in priority_cols:
            priority_cols.append(col)

    # Limit charts
    selected_cols = priority_cols[:max_charts]

    for col in selected_cols:
        fig, ax = plt.subplots(figsize=(5, 2.5))
        sns.histplot(df[col].dropna(), kde=True, ax=ax)
        ax.set_title(f"Distribution of {col}")
        yield fig




def plot_correlation(df, max_features=6):
    numeric_cols = df.select_dtypes(include="number").columns

    if len(numeric_cols) < 2:
        return None

    # Select top correlated features
    corr = df[numeric_cols].corr().abs()
    top_features = corr.sum().sort_values(ascending=False).head(max_features).index

    fig, ax = plt.subplots(figsize=(5, 2.5))
    sns.heatmap(
        df[top_features].corr(),
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        ax=ax
    )
    ax.set_title("Top Feature Correlations")
    return fig


# =====================================================
# PHASE 4 — STEP → TOOL MAPPING
# =====================================================
def execute_agent_step(step: str, df: pd.DataFrame, charts_container):
    step_lower = step.lower()

    if "structure" in step_lower or "dataset" in step_lower:
        return analyze_structure(df)

    if "missing" in step_lower:
        return analyze_missing_values(df)

    if "statistics" in step_lower or "summary" in step_lower:
        return analyze_statistics(df)

    if "distribution" in step_lower:
        count = 0
        for fig in plot_numeric_distributions(df, max_charts=5):
            with charts_container:
                st.pyplot(fig, use_container_width=False)
            count += 1

        return f"Plotted {count} key numeric distributions"


    if "correlation" in step_lower:
        fig = plot_correlation(df)
        if fig:
            charts_container.pyplot(fig, use_container_width=False)
            return "Plotted correlation heatmap"
        return "Not enough numeric columns for correlation"

    return "Step skipped (no matching tool)"


# =====================================================
# PHASE 4 — AGENT CONTROLLER
# =====================================================

def run_agent(eda_plan: str, df: pd.DataFrame, charts_container):
    results = []
    steps = [step.strip("- ").strip() for step in eda_plan.split("\n") if step.strip()]

    executed_actions = set()  # 🔒 prevents duplicate execution

    for step in steps:
        step_lower = step.lower()

        # ---- DISTRIBUTION (RUN ONCE) ----
        if "distribution" in step_lower:
            if "distribution" not in executed_actions:
                result = execute_agent_step(step, df, charts_container)
                executed_actions.add("distribution")
            else:
                result = "Skipped duplicate distribution step"
        
        # ---- CORRELATION (RUN ONCE) ----
        elif "correlation" in step_lower:
            if "correlation" not in executed_actions:
                result = execute_agent_step(step, df, charts_container)
                executed_actions.add("correlation")
            else:
                result = "Skipped duplicate correlation step"

        # ---- EVERYTHING ELSE (SAFE TO REPEAT) ----
        else:
            result = execute_agent_step(step, df, charts_container)

        results.append({"step": step, "result": result})

    return results


# =====================================================
# PHASE 5 — OBSERVATION BUILDER
# =====================================================

def build_observation_summary(df: pd.DataFrame):
    summary = {}

    # Basic shape
    summary["rows"] = df.shape[0]
    summary["columns"] = df.shape[1]

    # Missing value percentages
    missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
    summary["missing_percentage"] = missing_pct.to_dict()

    # Survival-specific metrics (if present)
    if "Survived" in df.columns:
        summary["overall_survival_rate_pct"] = round(df["Survived"].mean() * 100, 2)

        if "Sex" in df.columns:
            summary["survival_by_gender_pct"] = (
                df.groupby("Sex")["Survived"]
                .mean()
                .mul(100)
                .round(2)
                .to_dict()
            )

        if "Pclass" in df.columns:
            summary["survival_by_class_pct"] = (
                df.groupby("Pclass")["Survived"]
                .mean()
                .mul(100)
                .round(2)
                .to_dict()
            )

    # Fare stats
    if "Fare" in df.columns:
        summary["fare_stats"] = {
            "min": round(df["Fare"].min(), 2),
            "median": round(df["Fare"].median(), 2),
            "mean": round(df["Fare"].mean(), 2),
            "max": round(df["Fare"].max(), 2),
        }

    return summary



# =====================================================
# PHASE 5 — INSIGHT GENERATOR
# =====================================================
def generate_insights(user_goal: str, observation_summary: dict) -> str:
    prompt = f"""
You are a senior data analyst writing a factual EDA report.

STRICT RULES (MANDATORY):
- You may ONLY use the facts provided below.
- Every insight MUST reference at least one numeric value.
- You will be generating insights along with fact like a detective
- Do NOT use external knowledge (including Titanic history).
- Do NOT say "significant" or "many" without numbers.
- If a fact is missing, say it cannot be concluded.

FACTS (JSON):
{observation_summary}

USER GOAL:
{user_goal}

OUTPUT FORMAT:
- Use bullet points
- Each bullet must contain:
  • a numeric observation
  • why it matters analytically
- Be concise, precise, and factual
"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


# =====================================================
# PHASE 1 — UI
# =====================================================
st.title("📊 Auto EDA Agent")
st.write(
    "Upload a CSV dataset, describe your goal, "
    "and let an AI agent analyze your data end-to-end."
)

st.divider()

# Sidebar Inputs
st.sidebar.header("🔹 Input")

uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
user_goal = st.sidebar.text_area(
    "What is your goal?",
    placeholder="Example: Perform EDA and identify key patterns"
)
run_button = st.sidebar.button("🚀 Run Analysis")


# Output Sections
st.header("📄 Dataset Preview")
dataset_placeholder = st.empty()

st.header("📈 Charts")
charts_container = st.container()

st.header("🧠 Agent Reasoning")
reasoning_placeholder = st.empty()

st.header("💡 Insights")
insights_placeholder = st.empty()


# =====================================================
# MAIN AGENT PIPELINE (PHASES 1–5)
# =====================================================
if run_button:

    if uploaded_file is None:
        st.warning("Please upload a CSV file.")
        st.stop()

    if user_goal.strip() == "":
        st.warning("Please enter your goal.")
        st.stop()

    # Load dataset
    df = pd.read_csv(uploaded_file)

    # Dataset preview
    dataset_placeholder.subheader("First 5 Rows")
    dataset_placeholder.dataframe(df.head())

    dataset_placeholder.subheader("Dataset Shape")
    dataset_placeholder.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")

    dataset_placeholder.subheader("Data Types")
    dataset_placeholder.write(df.dtypes)

    dataset_placeholder.subheader("Missing Values")
    missing_df = df.isnull().sum().reset_index()
    missing_df.columns = ["Column", "Missing Values"]
    dataset_placeholder.dataframe(missing_df)


    # Agent Reasoning
    reasoning_placeholder.subheader("EDA Plan (Agent Reasoning)")
    with st.spinner("Agent is planning..."):
        eda_plan = generate_eda_plan(user_goal, df)
    reasoning_placeholder.code(eda_plan)

    # Agent Execution
    insights_placeholder.subheader("Agent Execution Log")
    with st.spinner("Agent is executing the plan..."):
        execution_results = run_agent(eda_plan, df, charts_container)

    for item in execution_results:
        insights_placeholder.write(f"**Step:** {item['step']}")
        insights_placeholder.write(item["result"])

    # Insight Generation
    insights_placeholder.subheader("🧠 AI-Generated Insights")
    observation_summary = build_observation_summary(df)

    with st.spinner("Agent is generating insights..."):
        insights_text = generate_insights(user_goal, observation_summary)

    insights_placeholder.markdown(insights_text)
