from custom_logging import logger


class LoggedException(Exception):
    def log(self):
        logger.error(self.args[0])
