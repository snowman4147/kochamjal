import logging
import sys
import os
from colorama import init, Fore, Style


init()


class ColorFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.msg = f"{Fore.BLUE}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.INFO:
            record.msg = f"{Fore.GREEN}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.CRITICAL:
            record.msg = f"{Fore.MAGENTA}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name, log_file, level=logging.INFO):
    logger = logging.getLogger(name)
    if not logger.handlers:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColorFormatter('%(asctime)s %(levelname)s: %(message)s'))
        logger.setLevel(level)
        logger.addHandler(handler)
        logger.addHandler(console_handler)
    return logger


preprocess_logger = setup_logger('preprocess_logger', '../logs/preprocess_logger.log')
