# -*- coding: utf-8 -*-

"""
Project Name: Crawler
File Created: 2024.05.23
Author: ZhangYuetao
GitHub: https://github.com/VerySeriousMan/Crawler
File Name: main.py
last renew 2024.05.29
"""

import toml
import colorlog
import requests
import chardet
from bs4 import BeautifulSoup
# 以上包用于直接对main.py情况下软件打包缺包的补充，复制其他子函数的包

import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5 import QtGui
import qt_material
import logging

from Crawler import Ui_MainWindow
from utils import pic_utils
from job_process import JobProcessor
from logger import logger


class MyClass(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyClass, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("图片爬虫软件V1.1")
        self.setWindowIcon(QtGui.QIcon("sunny.ico"))

        self.pic_utils_instance = pic_utils()
        self.job_processor = JobProcessor(self.pic_utils_instance)

        self.pic_path = None

        self.submit_button.clicked.connect(self.submit)
        self.pic_load_button.clicked.connect(self.pic_load)
        self.get_proxies_button.clicked.connect(self.refresh_proxies)
        self.stop_button.clicked.connect(self.stop_download)

        # 连接日志信息输出到 text_edit 控件
        log_handler = QTextEditLogger(self.log_edit)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.INFO)  # 设置日志级别

    def refresh_setting(self):
        keyword = self.keyword_edit.text()
        num = self.num_edit.text()
        save_address = self.save_address_edit.text()
        input_type = 'text'
        image_file = None
        if self.pic_path is not None:
            input_type = 'image'
            image_file = self.pic_path
            keyword = 'same_'+os.path.basename(self.pic_path).split('.')[0]
        self.pic_utils_instance.refresh_settings(
            keyword=keyword,
            download_folder=save_address,
            num_images=num,
            input_type=input_type,
            image_file=image_file
        )

    def pic_load(self):
        file_path = QFileDialog.getOpenFileName(self)[0]
        if (file_path.endswith('jpg') or file_path.endswith('jpeg')
                or file_path.endswith('png') or file_path.endswith('bmp')):
            self.pic_path = file_path
            logger.info(f"successfully loading pic: {file_path}.")
        else:
            logger.warning(f"{file_path} is not a valid image.")

    def refresh_proxies(self):
        self.pic_utils_instance.refresh_proxies()

    def submit(self):
        self.refresh_setting()
        settings = self.pic_utils_instance.get_settings()
        keyword = settings.get('keyword', 'default_keyword')
        download_folder = settings.get('download_folder', 'downloads')
        num_images = int(settings.get('num_images', 10))
        input_type = settings.get('input_type', 'text')
        image_file = settings.get('image_file', '')
        img_urls = None
        self.job_processor.terminate = False  # 打开

        if input_type == 'text':
            img_urls = self.job_processor.baidu_image_search(keyword)
        elif input_type == 'image':
            img_urls = self.job_processor.baidu_image_search_by_image(image_file)
        else:
            logger.error(f"{input_type} type error!")

        if img_urls:
            self.job_processor.download_images(img_urls[:num_images], keyword, download_folder)

    def stop_download(self):
        self.job_processor.terminate_download()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '二次确认', '确定要退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.stop_download()  # 调用停止下载方法
            event.accept()
        else:
            event.ignore()


# QTextEditLogger 类用于将日志信息输出到 QTextEdit 控件
class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        msg = self.format(record)
        color = self.get_color(record.levelname)
        html_msg = f'<span style="color:{color}">{msg}</span>'
        self.text_edit.append(html_msg)
        # 强制刷新QTextEdit
        self.text_edit.ensureCursorVisible()
        self.text_edit.repaint()

    def get_color(self, levelname):
        colors = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'orange',
            'ERROR': 'red',
            'CRITICAL': 'darkred',
        }
        return colors.get(levelname, 'black')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyClass()
    qt_material.apply_stylesheet(app, theme='default')
    myWin.show()
    sys.exit(app.exec_())
