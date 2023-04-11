import logging


class LoggerUtil:

    @staticmethod
    def get_logger(name, log_level=logging.DEBUG):
        logger = logging.getLogger(name)
        logger.setLevel(log_level)

        # Create a console handler and set its log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create a formatter and set it for the console handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        logger.addHandler(console_handler)

        return logger
