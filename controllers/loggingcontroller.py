import logging
import io


class LoggingController(object):

    def __init__(self):
        logger = logging.getLogger("Provenance")
        logger.setLevel(logging.WARNING)
        formatter = logging.Formatter(fmt="%(asctime)s: [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        self._logger: logging.Logger = logger
        self._formatter: logging.Formatter = formatter
        file_handler = logging.FileHandler("logs/provenance.log")
        file_handler.setLevel(logging.CRITICAL)
        file_handler.setFormatter(self._formatter)
        self._logger.addHandler(file_handler)

        self._text_stream = io.StringIO()
        output_handler = logging.StreamHandler(self._text_stream)
        output_handler.setFormatter(self._formatter)
        file_handler.setLevel(logging.CRITICAL)
        self._logger.addHandler(output_handler)


