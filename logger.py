# -*- coding: utf-8 -*-

"""
Project Name: Crawler
File Created: 2024.05.27
Author: ZhangYuetao
GitHub: https://github.com/VerySeriousMan/Crawler
File Name: logger.py
last renew 2024.05.28
"""

import logging
import os
from datetime import datetime
import colorlog

log_folder = "log"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# 生成日志文件名
log_filename = os.path.join(log_folder, datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "_log.txt")

# 配置日志记录
log_format = "%(asctime)s - %(levelname)s - %(message)s"
color_log_format = "%(log_color)s%(asctime)s - %(levelname)s - %(message)s"

file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format))

stream_handler = colorlog.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(colorlog.ColoredFormatter(
    color_log_format,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Example usage
if __name__ == "__main__":
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
