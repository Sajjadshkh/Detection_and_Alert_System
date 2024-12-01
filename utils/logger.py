import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

def log_warning(message):
    logging.warning(message)