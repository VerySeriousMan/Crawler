# -*- coding: utf-8 -*-
"""
Project Name: Crawler
File Created: 2024.11.18
Author: ZhangYuetao
File Name: server_connect.py
Update: 2024.11.18
"""

import os
import subprocess
import sys
import time

import toml
import shutil

import smbclient


def load_credentials(config_path=r"setting/.secret.toml"):
    with open(config_path, 'r') as config_file:
        config = toml.load(config_file)
        credentials = config.get("credentials", {})
        return (
            credentials.get("server_ip"),
            credentials.get("share_name"),
            credentials.get("username"),
            credentials.get("password"),
        )


def get_current_software_version(current_software_path):
    file_dir = os.path.dirname(current_software_path)
    file_path = os.path.join(file_dir, 'setting', 'software_infos.toml')

    try:
        with open(file_path, mode='r') as f:
            file_content = f.read()  # 读取文件内容

        # 解析 TOML 文件
        toml_data = toml.loads(file_content)

        # 提取 version 信息
        version = toml_data.get("version", "未知")
        return version
    except:
        return '未知'


def get_update_log(software_name):
    # 从 .secret.toml 中加载配置信息
    server_ip, share_name, username, password = load_credentials()

    # 注册会话
    smbclient.register_session(server_ip, username=username, password=password)

    # 构建共享路径
    share_path = f"\\\\{server_ip}\\{share_name}"

    share_dir = r"数据相关软件/数据处理软件"
    file_dir = os.path.join(share_path, share_dir)

    # 读取文件内容
    try:
        txt_path = None
        files = smbclient.listdir(file_dir)
        for dir_name in files:
            if software_name in dir_name and 'linux' not in dir_name:
                software_dir = os.path.join(file_dir, dir_name)
                txt_path = os.path.join(software_dir, 'update_log.txt')
                break

        if not txt_path:
            raise FileNotFoundError("未找到txt对应文件")

        with smbclient.open_file(txt_path, mode='r', encoding='utf-8') as file:
            txt_content = file.read()

        return txt_content

    except Exception as e:
        raise ValueError(f"读取文件出错: {e}")


def get_new_software_version(software_name):
    # 从 .secret.toml 中加载配置信息
    server_ip, share_name, username, password = load_credentials()

    # 注册会话
    smbclient.register_session(server_ip, username=username, password=password)

    # 构建共享路径
    share_path = f"\\\\{server_ip}\\{share_name}"

    share_dir = r"数据相关软件/数据处理软件"
    file_dir = os.path.join(share_path, share_dir)

    # 读取文件内容
    try:
        toml_path = None
        files = smbclient.listdir(file_dir)
        for dir_name in files:
            if software_name in dir_name and 'linux' not in dir_name:
                software_dir = os.path.join(file_dir, dir_name)
                toml_path = os.path.join(software_dir, 'setting', 'software_infos.toml')
                break

        if not toml_path:
            raise FileNotFoundError("未找到对应文件")

        with smbclient.open_file(toml_path, mode='r') as file:
            toml_content = file.read()

        # 解析 TOML 文件
        toml_data = toml.loads(toml_content)

        # 提取 version 信息
        version = toml_data.get("version", "未找到 version 信息")
        return version
    except Exception as e:
        raise ValueError(f"读取文件出错: {e}")


def update_software(software_dir, software_name):
    server_ip, share_name, username, password = load_credentials()

    # 注册会话
    smbclient.register_session(server_ip, username=username, password=password)

    # 构建共享路径
    share_path = f"\\\\{server_ip}\\{share_name}"

    share_dir = r"数据相关软件/数据处理软件"
    file_dir = os.path.join(share_path, share_dir)

    # 读取文件内容
    try:
        files = smbclient.listdir(file_dir)
        update_software_dir = None
        for dir_name in files:
            if software_name in dir_name and 'linux' not in dir_name:
                update_software_dir = os.path.join(file_dir, dir_name)
                break

        if not update_software_dir:
            raise FileNotFoundError("未找到对应软件")

        new_software_path = None

        for root, dirs, files in smbclient.walk(update_software_dir):
            files = [f for f in files if not f.startswith('.')]  # 排除隐藏文件
            for file in files:
                if file.endswith('.exe'):
                    new_software_path = os.path.join(root, file)
                    temp_dir = os.path.join(software_dir, 'temp')
                    os.makedirs(temp_dir, exist_ok=True)
                    shutil.copy2(new_software_path, temp_dir)
                    new_software_path = os.path.join(temp_dir, file)
                else:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(software_dir, os.path.relpath(src_file, update_software_dir))
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)

        if new_software_path and is_file_complete(new_software_path):
            subprocess.Popen(new_software_path)
            time.sleep(1)
            sys.exit("程序已退出")

    except Exception as e:
        raise ValueError(f"读取文件出错: {e}")


def is_file_complete(file_path, timeout=60):
    """检查文件是否完全复制完成"""
    if not os.path.exists(file_path):
        return False

    initial_size = os.path.getsize(file_path)
    time.sleep(1)  # 等待1秒钟，给文件写入一些时间
    final_size = os.path.getsize(file_path)

    # 如果文件大小没有变化，认为文件已复制完成
    if initial_size == final_size:
        return True

    # 如果文件大小仍在变化，则继续等待
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(1)
        new_size = os.path.getsize(file_path)
        if new_size == final_size:
            return True
        final_size = new_size

    # 超过最大等待时间后认为文件未复制完成
    return False


def check_version(current_version):
    try:
        new_version = get_new_software_version('图片爬虫软件')
    except:
        new_version = '未知'

    if new_version != '未知':
        if current_version != new_version:
            return 1
        else:
            return 0
    else:
        return -1
