# -*- coding: utf-8 -*-

"""
Project Name: Crawler
File Created: 2024.05.23
Author: ZhangYuetao
File Name: main.py
Update: 2024.11.18
"""

import os
import shutil
import subprocess
import sys
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import QtGui, QtCore
import qt_material
import logging

from Crawler import Ui_MainWindow
from utils import pic_utils
from job_process import JobProcessor
from logger import logger
import server_connect


class MyClass(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyClass, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("图片爬虫软件V1.3")
        self.setWindowIcon(QtGui.QIcon("sunny.ico"))

        self.pic_utils_instance = pic_utils()
        self.job_processor = JobProcessor(self.pic_utils_instance)

        self.pic_path = None
        self.time_settings_path = 'setting/time_settings.toml'
        self.current_software_path = self.get_file_path()
        self.current_software_version = server_connect.get_current_software_version(self.current_software_path)

        self.submit_button.clicked.connect(self.submit)
        # self.pic_load_button.clicked.connect(self.pic_load)
        # self.get_proxies_button.clicked.connect(self.refresh_proxies)
        self.stop_button.clicked.connect(self.stop_download)
        self.software_update_action.triggered.connect(self.update_software)

        self.web = 'baidu'
        self.web_select_box.addItems(['baidu', 'bing', 'sogou', '360'])
        self.web_select_box.currentIndexChanged.connect(self.select_web)

        # 连接日志信息输出到 text_edit 控件
        log_handler = QTextEditLogger(self.log_edit)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.INFO)  # 设置日志级别

        self.auto_update()
        self.init_update()

    def init_update(self):
        dir_path = os.path.dirname(self.current_software_path)
        dir_name = os.path.basename(dir_path)
        if dir_name == 'temp':
            old_dir_path = os.path.dirname(dir_path)
            for file in os.listdir(old_dir_path):
                if file.endswith('.exe'):
                    old_software = os.path.join(old_dir_path, file)
                    os.remove(old_software)
            shutil.copy2(self.current_software_path, old_dir_path)
            new_file_path = os.path.join(old_dir_path, os.path.basename(self.current_software_path))
            if os.path.exists(new_file_path) and server_connect.is_file_complete(new_file_path):
                msg_box = QMessageBox(self)  # 创建一个新的 QMessageBox 对象
                reply = msg_box.question(self, '更新完成', '软件更新完成，需要立即重启吗？',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                msg_box.raise_()  # 确保弹窗显示在最上层

                if reply == QMessageBox.Yes:
                    subprocess.Popen(new_file_path)
                    time.sleep(1)
                    sys.exit("程序已退出")
                else:
                    sys.exit("程序已退出")
        else:
            is_updated = 0
            for file in os.listdir(dir_path):
                if file == 'temp':
                    is_updated = 1
                    shutil.rmtree(file)
            if is_updated == 1:
                try:
                    text = server_connect.get_update_log('图片爬虫软件')
                    QMessageBox.information(self, '更新成功', f'更新成功！\n{text}')
                except Exception as e:
                    QMessageBox.critical(self, '更新成功', f'日志加载失败: {str(e)}')

    @staticmethod
    def get_file_path():
        # 检查是否是打包后的程序
        if getattr(sys, 'frozen', False):
            # PyInstaller 打包后的路径
            current_path = os.path.abspath(sys.argv[0])
        else:
            # 非打包情况下的路径
            current_path = os.path.abspath(__file__)
        return current_path

    def auto_update(self):
        dir_path = os.path.dirname(self.current_software_path)
        dir_name = os.path.basename(dir_path)
        if dir_name != 'temp':
            if server_connect.check_version(self.current_software_version) == 1:
                self.update_software()

    def update_software(self):
        update_way = server_connect.check_version(self.current_software_version)
        if update_way == -1:
            # 网络未连接，弹出提示框
            QMessageBox.warning(self, '更新提示', '网络未连接，暂时无法更新')
        elif update_way == 0:
            # 当前已为最新版本，弹出提示框
            QMessageBox.information(self, '更新提示', '当前已为最新版本')
        else:
            # 弹出提示框，询问是否立即更新
            msg_box = QMessageBox(self)  # 创建一个新的 QMessageBox 对象
            reply = msg_box.question(self, '更新提示', '发现新版本，开始更新吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            msg_box.raise_()  # 确保弹窗显示在最上层

            if reply == QMessageBox.Yes:
                try:
                    server_connect.update_software(os.path.dirname(self.current_software_path), '图片爬虫软件')
                    text = server_connect.get_update_log('图片爬虫软件')
                    QMessageBox.information(self, '更新成功', f'更新成功！\n{text}')
                except Exception as e:
                    QMessageBox.critical(self, '更新失败', f'更新失败: {str(e)}')
            else:
                pass

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

    # def pic_load(self):
    #     file_path = QFileDialog.getOpenFileName(self)[0]
    #     if (file_path.endswith('jpg') or file_path.endswith('jpeg')
    #             or file_path.endswith('png') or file_path.endswith('bmp')):
    #         self.pic_path = file_path
    #         logger.info(f"successfully loading pic: {file_path}.")
    #     else:
    #         logger.warning(f"{file_path} is not a valid image.")

    # def refresh_proxies(self):
    #     self.pic_utils_instance.refresh_proxies()

    def submit(self):
        self.refresh_setting()
        settings = self.pic_utils_instance.get_settings(self.pic_utils_instance.settings_path)
        keyword = settings.get('keyword', 'default_keyword')
        download_folder = settings.get('download_folder', 'downloads')
        num_images = int(settings.get('num_images', 10))
        input_type = settings.get('input_type', 'text')
        image_file = settings.get('image_file', '')
        img_urls = None
        self.job_processor.terminate = False  # 打开

        if self.web == 'baidu':
            img_urls = self.job_processor.baidu_image_search(keyword, int(num_images / 30 + 1))
        elif self.web == 'bing':
            img_urls = self.job_processor.bing_image_search(keyword, int(num_images / 35 + 1))
        elif self.web == 'sogou':
            img_urls = self.job_processor.sogou_image_search(keyword, int(num_images / 48 + 1))
        elif self.web == '360':
            img_urls = self.job_processor.so_image_search(keyword, int(num_images / 30 + 1))

        # elif input_type == 'image':
        #     img_urls = self.job_processor.baidu_image_search_by_image(image_file)
        # else:
        #     logger.error(f"{input_type} type error!")

        if img_urls:
            time_settings = self.pic_utils_instance.get_settings(self.time_settings_path)
            download_way = time_settings.get('download_way', 0)
            if download_way == 0:
                self.job_processor.download_images(img_urls[:num_images], keyword, self.web, download_folder)
            if download_way == 1:
                self.job_processor.threads_download_images(img_urls[:num_images], keyword, self.web, download_folder)
            else:
                logger.error(f"{download_way} type error!")

    def stop_download(self):
        self.job_processor.terminate_download()

    def select_web(self):
        self.web = self.web_select_box.currentText()

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
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)  # 自适应适配不同分辨率
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    myWin = MyClass()
    qt_material.apply_stylesheet(app, theme='default')
    myWin.show()
    sys.exit(app.exec_())
