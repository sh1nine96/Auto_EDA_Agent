import logging

# Set up logging configuration
logging.basicConfig(filename='error_log.log', level=logging.ERROR)

class CustomError(Exception):
    """Base class for all custom exceptions"""
    pass

class DatabaseConnectionError(CustomError):
    """Raised when there is a database connection error"""
    def __init__(self, message='Database connection failed. Please check your settings.'): 
        self.message = message
        super().__init__(self.message)

class FileNotFoundError(CustomError):
    """Raised when a requested file is not found"""
    def __init__(self, filename): 
        self.message = f'File {filename} was not found. Please verify the file path.'
        super().__init__(self.message)

class InvalidInputError(CustomError):
    """Raised when the input provided is invalid"""
    def __init__(self, input_value): 
        self.message = f'Invalid input: {input_value}. Please provide valid input.'
        super().__init__(self.message)

def log_error(error):
    """Logs an error message to the error log file"""
    logging.error(f'{error}')

# Example of using the custom error and logging function
if __name__ == '__main__':
    try:
        raise DatabaseConnectionError()
    except CustomError as e:
        log_error(e)  # Log the error
        print(e)  # User-friendly message
