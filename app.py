# Comprehensive Error Handling in app.py

import logging
import sys

# Setting up logging
logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class CustomException(Exception):
    """Custom Exception to handle application specific errors"""
    pass

def some_function():
    """A function that might throw an error"""
    try:
        # Simulating some work
        logging.info("Function 'some_function' started.")
        result = 10 / 0  # This will raise a ZeroDivisionError
        logging.info("Function 'some_function' completed successfully.")
        return result
    except ZeroDivisionError as e:
        logging.error(f"Error occurred: {e}")
        raise CustomException("An error occurred in part of the process, please check logs.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise CustomException("An unexpected error occurred, please check logs.")

if __name__ == '__main__':
    try:
        logging.info("Application started.")
        result = some_function()
    except CustomException as e:
        logging.critical(f"Critical error: {e}")
        print("An error occurred, please consult the logs for more details.")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}")
        print("An unexpected error occurred, please consult the logs for more details.")
        sys.exit(1)
    logging.info("Application finished successfully.")