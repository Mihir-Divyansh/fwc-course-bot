import logging

formatter = logging.Formatter('%(levelname)s[%(asctime)s]: %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    log = logging.getLogger(name)
    log.setLevel(level)
    log.addHandler(handler)

    return log

# all logs are in logs folder
log = setup_logger('default-logs', 'logs/default')
cmd = setup_logger('command-logs', 'logs/command')

