import os
import logging
import logging.config
import logging.handlers

def get_logger(file_name):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # if file_name[0] != 'v' else "../../logs/{}.log".format(file_name)
    current_dir = os.getcwd()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(root_dir, ".git")):
        root_dir = os.path.dirname(root_dir)

    if current_dir == root_dir:
        file = "logs/{}.log".format(file_name) 
    else:
        file = "../../logs/{}.log".format(file_name)
    
    file_handler = logging.handlers.RotatingFileHandler(file, maxBytes=10485760, backupCount=1)
    # change this for different logging levels:
        # INFO, WARNING, DEBUG, ERROR, CRITICAL
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    with open(file, "w") as f:
        f.truncate(0)
    return logger