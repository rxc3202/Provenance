from datetime import datetime
import logging
import os


class LoggingController(object):

    logfile_date_format = "%Y-%m-%d %H:%M:%S"
    ui_date_format = "%H:%M:%S"

    def __init__(self, logfile):
        self._log_level = logging.INFO
        # Set up logger
        logger = logging.getLogger("Provenance")
        self._logger: logging.Logger = logger
        self._old_factory = logging.getLogRecordFactory()
        logger.setLevel(self._log_level)
        formatter = logging.Formatter(fmt="%(asctime)s: [%(levelname)s] %(message)s",
                                      datefmt=self.logfile_date_format)
        self._formatter: logging.Formatter = formatter
        # set new logging factory to inject fields into logger
        factory = self._generate_record_factory()
        logging.setLogRecordFactory(factory)

        # Generate File handler to log output to file
        cwd = os.getcwd()
        path = os.path.join(cwd, logfile)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Set a filter as a janky hooking call to get all the new records
        # so that the UI can display client-server interactions
        self._filter = ProvenanceLoggingFilter()
        logger.addFilter(self._filter)

    def _generate_record_factory(self):
        """
        Generate a new record factory that will inject the creation time
        of the record in order to do filtering based on time
        :return: a function specified by python3 logging.getLoggingRecordFactory()
        """
        def record_factory(*args, **kwargs) -> logging.LogRecord:
            record = self._old_factory(*args, **kwargs)
            # inject the "create_time" field into all records
            record.creation_time = datetime.now()
            return record
        return record_factory

    def get_messages(self):
        records = self._filter.records
        return [f"{r.creation_time.strftime(self.ui_date_format)} [{r.levelname}] {r.msg}" for r in records]

    @property
    def log_level(self):
        return self._log_level

    @log_level.setter
    def log_level(self, level):
        self._log_level = level
        self._logger.setLevel(level)


class ProvenanceLoggingFilter(logging.Filter):

    _last_time = datetime.now()

    def __init__(self):
        super().__init__()
        self._records = []

    def filter(self, record: logging.LogRecord) -> int:
        """
        The custom function used to filter records. However, there is no
        way to selectively pick records, so we will use this as a hook to
        pass only the newest logs to the model to be queried by the ui interfaces
        :param record: the logging.LogRecord Object
        :return: 0 if should be filtered else non-zero
        """
        if record.creation_time >= self._last_time:
            self._last_time = datetime.now()
            # Call function
            self._records.append(record)
        return super().filter(record)

    @property
    def records(self):
        records = self._records.copy()
        self._records.clear()
        return records
