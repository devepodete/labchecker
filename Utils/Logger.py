import logging


class Logger:
    def __init__(self, file=None):
        if not file:
            return
        self.file = file
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        fh = logging.FileHandler(file)
        formatter = logging.Formatter('[%(asctime)s] - %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def log(self, message: str, level=logging.INFO):
        if not self.file:
            return
        self.logger.log(level, message)
