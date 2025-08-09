"""
Centralized logging configuration
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Create logs directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class SafeStreamHandler(logging.StreamHandler):
    """Stream handler that handles Unicode properly"""

    def emit(self, record):
        try:
            msg = self.format(record)
            try:
                msg.encode(sys.stdout.encoding)
            except UnicodeEncodeError:
                msg = msg.encode('ascii', 'ignore').decode('ascii')
            self.stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logging():
    """Configure application-wide logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with Unicode support
    console_handler = SafeStreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_DIR / "tinder_bot.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8',
        errors='ignore'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_formatter)
    root_logger.addHandler(file_handler)

    # Suppress noisy libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    # Log that logging is configured
    root_logger.info("🔧 Logging configured successfully")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def safe_log_info(message: str):
    """Log message safely, handling Unicode"""
    logger = logging.getLogger()
    try:
        logger.info(message)
    except UnicodeEncodeError:
        logger.info(message.encode('ascii', 'ignore').decode('ascii'))