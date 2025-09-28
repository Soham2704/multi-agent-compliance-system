import logging
import json
import os
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """
    Custom formatter to output log records as structured JSON.
    This is a standard practice for creating machine-readable logs.
    """
    def format(self, record):
        # Create a base log record with a standard ISO 8601 timestamp
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "source": record.name
        }
        # If the log call includes 'extra' data, add it to the record
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
            
        return json.dumps(log_record)

def setup_logger(name='MultiAgentSystem', log_file='reports/agent_log.jsonl'):
    """
    Sets up a logger that writes to a specified file with the JSON formatter.
    """
    # Create the 'reports' directory if it doesn't exist to avoid errors
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent logs from being duplicated in the console output
    logger.propagate = False

    # Clear any existing handlers to prevent duplicate log entries on re-runs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create file handler which logs messages in append mode
    fh = logging.FileHandler(log_file, mode='a')
    fh.setLevel(logging.INFO)

    # Create our custom JSON formatter and add it to the handler
    formatter = JsonFormatter()
    fh.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(fh)

    return logger

# Create a single, global logger instance that the rest of our application can import and use
logger = setup_logger()
