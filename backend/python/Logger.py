import logging
from logging.handlers import RotatingFileHandler

from backend.python.location.Location import Location


class Logger:
    _logger = None

    def __init__(self, logpath, filename, print=True, write=False):
        if Logger._logger is None:
            debug_level = logging.INFO
            logging.basicConfig(
                                level=debug_level,
                                format='%(message)s',
                                # format='%(levelname)s %(asctime)s %(message)s',
                                datefmt='%m/%d/%Y%I:%M:%S %p')

            Logger._logger = logging.getLogger('my_logger')
            Logger._logger.propagate = False

            if print:
                ch = logging.StreamHandler()
                ch.setLevel(logging.WARN)
                Logger._logger.addHandler(ch)

            if write:
                fh = logging.FileHandler(logpath + filename)
                fh.setLevel(debug_level)
                Logger._logger.addHandler(fh)
            # Logger._logger.addHandler(RotatingFileHandler(
            #     filename=logpath + filename,
            #     mode='a',
            #     maxBytes=512000,
            #     backupCount=4))

    def log(self, message, _type='d'):
        if _type == 'd':
            Logger._logger.debug(message)
        elif _type == 'i':
            Logger._logger.info(message)
        elif _type == 'w':
            Logger._logger.warn(message)
        elif _type == 'e':
            Logger._logger.error(message)
        elif _type == 'c':
            Logger._logger.critical(message)


    def log_location(self, loc):
        self.log(loc.__repr__(), 'i')

    def log_person(self, p):
        self.log(p.__repr__(), 'i')

    def log_graph(self, root):
        def f(r: Location):
            self.log_location(r)
            for ch in r.locations:
                f(ch)

        f(root)

    def log_people(self, people):
        for p in people:
            self.log_person(p)

    def close(self):
        # Shut down the logger
        logging.shutdown()
