import logging


class MyFileHandler(logging.FileHandler):
    def emit(self, record):
        if record.levelno == self.level:
            super().emit(record)


class MyStreamHandler(logging.StreamHandler):
    def __init__(self, skip_print):
        super().__init__()
        self.skip = skip_print

    def emit(self, record):
        if record.levelno != self.skip:
            super().emit(record)


class Logger:
    _logger = None
    write_level = None
    write_level_ = None

    def __init__(self, logpath, filename, print=True, write=False):
        if Logger._logger is None:
            Logger.write_level = 'i'
            Logger.write_level_ = logging.INFO

            logging.basicConfig(
                level=logging.DEBUG,
                format='%(message)s',
                # format='%(levelname)s %(asctime)s %(message)s',
                datefmt='%m/%d/%Y%I:%M:%S %p')

            Logger._logger = logging.getLogger('my_logger')
            Logger._logger.propagate = False

            if print:
                ch = MyStreamHandler(Logger.write_level_)
                ch.setLevel(logging.CRITICAL)
                Logger._logger.addHandler(ch)

            if write:
                fh = MyFileHandler(logpath + filename)
                fh.setLevel(Logger.write_level_)
                Logger._logger.addHandler(fh)

    @staticmethod
    def log(message, _type='d'):
        if _type == 'd':
            Logger._logger.debug('D: ' + message)
        elif _type == 'i':
            Logger._logger.info('I: ' + message)
        elif _type == 'w':
            Logger._logger.warn('W: ' + message)
        elif _type == 'e':
            Logger._logger.error('E: ' + message)
        elif _type == 'c':
            Logger._logger.critical('C: ' + message)

    @staticmethod
    def log_location(loc):
        Logger.log(loc.__repr__(), Logger.write_level)

    @staticmethod
    def log_person(p):
        Logger.log(p.__repr__(), Logger.write_level)

    @staticmethod
    def log_graph(root):
        def f(r):
            Logger.log_location(r)
            for ch in r.locations:
                f(ch)

        f(root)

    @staticmethod
    def log_people(people):
        for p in people:
            Logger.log_person(p)

    @staticmethod
    def close():
        # Shut down the logger
        logging.shutdown()
