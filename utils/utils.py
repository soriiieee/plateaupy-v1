import logging
import datetime
import json
import os
import io
import time
import requests

def file_logger(log_path):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    os.makedirs(log_path, exist_ok=True)
    log_file = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.log'
    log_file = os.path.join(log_path, log_file)
    fh = logging.FileHandler(filename=log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s[%(levelname)s] - %(message)s"))
    logger.addHandler(fh)
    return logger


def write_json_file(target, output_dir):
    with open(output_dir, 'w') as f:
        json.dump(target, f)

