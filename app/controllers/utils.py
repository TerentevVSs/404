import logging


def get_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    f_handler = logging.FileHandler(filename)
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)

    c_handler = logging.StreamHandler()
    c_handler.setFormatter(f_format)
    c_handler.setLevel(logging.DEBUG)
    logger.addHandler(c_handler)

    return logger
