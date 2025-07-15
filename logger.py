import inspect
import logging
import os
import sys
import traceback


class CustomFormatter(logging.Formatter):
    """
    Custom formatter for console logs that applies colored output
    based on the log level (DEBUG, INFO, ERROR).
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    format = "%(asctime)s | %(levelname)s | %(message)s"

    Formats = {
        logging.DEBUG: ''.join([grey, format]),
        logging.INFO: ''.join([yellow, format]),
        logging.ERROR: ''.join([red, format])
    }

    def format(self, record):
        """
        Overrides the default format method to apply custom styling.

        Args:
            record (LogRecord): The log record to format.

        Returns:
            str: The formatted log string.
        """
        log_fmt = self.Formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    """
    Adds functionality like log file separation, colored console output,
    and automatic function/file tagging.
    """

    def __init__(self, name=None):
        """
        Initializes the Logger instance.

        Args:
            name (str, optional): Name for the logger. Defaults to None.
        returns: None
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.log_path = None
        self.stream_handler = None

    def setup_logger_file(self, path, device=''):
        """
        Sets up log files for DEBUG, INFO, and ERROR levels separately
        and initializes colored console output.

        Args:
            path (str): Directory path where log files will be saved.
            device (str, optional): Optional device prefix for log files.
        returns: None
        """
        self.log_path = path
        log_format = "%(asctime)s | %(levelname)s | %(message)s"
        formatter = logging.Formatter(log_format)

        if device:
            device = '_'.join([device, ''])

        debug_path = os.path.join(self.log_path, f"{device}debug.log")
        debug_handler = logging.FileHandler(debug_path)
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        self.logger.addHandler(debug_handler)

        error_path = os.path.join(self.log_path, f"{device}error.log")
        error_handler = logging.FileHandler(error_path)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

        info_path = os.path.join(self.log_path, f"{device}info.log")
        info_handler = logging.FileHandler(info_path)
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        self.logger.addHandler(info_handler)

        if not self.stream_handler:
            self.stream_handler = logging.StreamHandler(sys.stdout)
            self.stream_handler.setLevel(logging.DEBUG)
            self.stream_handler.setFormatter(CustomFormatter())
            self.logger.addHandler(self.stream_handler)

    def cleanup_logger(self, name):
        """
        Removes all log handlers from the logger.

        Args:
            name (str): The logger's name to clean up.
        returns: None
        """
        self.logger = logging.getLogger(name)
        while self.logger.handlers:
            if isinstance(self.logger.handlers[0], logging.StreamHandler):
                self.stream_handler = None
            self.logger.removeHandler(self.logger.handlers[0])

    def get_logger(self, name):
        """
        Sets or updates the logger instance by name.

        Args:
            name (str): Logger name.
        returns: None
        """
        self.logger = logging.getLogger(name)

    def function_property(self):
        """
        Gets the caller's function name and file name for context-aware logging.

        Args : None
        Returns:
            tuple: (function_name, file_name)
        """
        function = inspect.currentframe().f_back.f_back.f_code
        function_name = function.co_name
        filename = os.path.splitext(function.co_filename.split('/')[-1])[0]
        return function_name, filename

    def info(self, message):
        """
        Logs an INFO-level message with context.

        Args:
            message (str): The message to log.
        returns: None
        """
        function_name, filename = self.function_property()
        self.logger.info("%s | %s | %s" % (filename, function_name, message))

    def debug(self, message):
        """
        Logs a DEBUG-level message with context.

        Args:
            message (str): The message to log.
        returns: None
        """
        function_name, filename = self.function_property()
        self.logger.debug("%s | %s | %s" % (filename, function_name, message))

    def error(self, message):
        """
        Logs an ERROR-level message with context and full traceback.

        Args:
            message (str): The error message to log.
        returns: None
        """
        function_name, filename = self.function_property()
        self.logger.error("%s | %s | %s" % (filename, function_name, message))
        self.logger.error(traceback.format_exc())
