# -*- coding: utf-8 -*-

"""
备份
Project Name: Crawler
File Created: 2024.05.23
Author: ZhangYuetao
GitHub: https://github.com/VerySeriousMan/Crawler
File Name: pic.py
last renew 2024.05.24
"""
"""
import re
import requests
import os
import time
import random
import json
import toml
from bs4 import BeautifulSoup
import logging
from datetime import datetime


# 创建日志文件夹
log_folder = "log"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# 生成日志文件名
log_filename = os.path.join(log_folder, datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + "_log.txt")

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def get_user_agents():
    try:
        with open("lake/user_agents.txt", "r") as file:
            user_agents = [line.strip() for line in file if line.strip()]
        return user_agents
    except FileNotFoundError:
        logger.error("User-Agent file not found.")
        return []


def get_random_user_agent():
    user_agents = get_user_agents()
    return random.choice(user_agents) if user_agents else None


# 从文件中读取代理列表
def get_proxies():
    try:
        with open("lake/proxies.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
        return proxies
    except FileNotFoundError:
        logger.error("Proxies file not found.")
        return []


def get_random_proxy():
    proxies = get_proxies()
    return random.choice(proxies) if proxies else None


# 从文件中读取查询参数
def get_params():
    try:
        with open("setting/param.json", "r") as file:
            params = json.load(file)
        return params
    except FileNotFoundError:
        logger.error("Params file not found.")
        return {}
    except json.JSONDecodeError:
        logger.error("Error decoding params file.")
        return {}


# 从 settings.toml 文件中读取设置
def get_settings():
    try:
        with open("setting/settings.toml", "r") as file:
            settings = toml.load(file)
        return settings
    except FileNotFoundError:
        logger.error("Settings file not found.")
        return {}
    except toml.TomlDecodeError:
        logger.error("Error decoding settings file.")
        return {}


# 在百度图片中搜索图片
def baidu_image_search(keyword):
    search_url = "https://image.baidu.com/search/index?tn=baiduimage&word="
    headers = {
        "User-Agent": get_random_user_agent(),
    }
    params = get_params()
    params['queryWord'] = keyword
    params['word'] = keyword

    all_urls = []

    for pn in range(10):
        params['pn'] = str(int(pn + 1) * 30)
        proxy = {'http': get_random_proxy()}
        try:
            logger.info(f"Trying proxy: {proxy}")
            response = requests.get(search_url, headers=headers, params=params, proxies=proxy, timeout=10)
            logger.info(f"Response status code: {response.status_code}")
            response.encoding = 'utf-8'
            html = response.text
            img_urls = re.findall('"thumbURL":"(.*?)",', html, re.S)
            logger.info(f"Found image URLs: {img_urls}")
            all_urls.extend(img_urls)
        except Exception as e:
            logger.error(f"Image search failed with proxy {proxy}: {e}")
            continue

    return all_urls


def baidu_image_search_by_image(image_path):
    upload_url = "https://graph.baidu.com/upload"
    headers = {
        "User-Agent": get_random_user_agent(),
    }

    # 上传图片获取图片 URL
    try:
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            proxy = {'http': get_random_proxy()}

            logger.info(f"Trying proxy: {proxy} for image upload")
            response = requests.post(upload_url, headers=headers, files=files, proxies=proxy, timeout=10)
            logger.info(f"Response status code for upload: {response.status_code}")
            response_data = response.json()
            logger.info(f"Response data for upload: {response_data}")

            if response_data.get('status') != 0:
                logger.error(f"Image upload failed with error: {response_data.get('msg')}")
                return []

            img_search_url = response_data['data']['url']
            logger.info(f"Uploaded image search URL: {img_search_url}")
    except Exception as e:
        logger.error(f"Image upload failed with proxy {proxy}: {e}")
        return []

    # 确保解析返回的 HTML 内容正确
    all_urls = []
    try:
        logger.info(f"Trying proxy: {proxy} for image search")
        response = requests.get(img_search_url, headers=headers, proxies=proxy, timeout=10)
        logger.info(f"Response status code: {response.status_code}")
        response.encoding = 'utf-8'
        html = response.text

        # 使用 BeautifulSoup 解析 HTML 页面
        soup = BeautifulSoup(html, "html.parser")

        # 查找所有图片标签
        img_tags = soup.find_all("img")

        # 提取图片链接
        img_urls = [img.get("src") for img in img_tags if img.get("src")]

        logger.info(f"Found image URLs: {img_urls}")
        all_urls.extend(img_urls)
    except Exception as e:
        logger.error(f"Image search failed with proxy {proxy}: {e}")

    return all_urls


# 下载图片
def download_images(img_urls, keyword, download_path):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    for idx, img_url in enumerate(img_urls):
        headers = {
            "User-Agent": get_random_user_agent(),
        }
        proxies = get_proxies()
        for proxy in proxies:
            try:
                logger.info(f"Trying proxy: {proxy}")
                img_data = requests.get(img_url, headers=headers, proxies={"http": proxy}, timeout=10).content
                logger.info(f"Downloaded image data size: {len(img_data)}")
                with open(os.path.join(download_path, f"{keyword}_{idx + 1}.jpg"), 'wb') as img_file:
                    img_file.write(img_data)
                logger.info(f"Downloaded {keyword}_{idx + 1}.jpg")
                break
            except Exception as e:
                logger.error(f"Failed to download {img_url} with proxy {proxy}: {e}")
                continue

        time.sleep(random.uniform(1, 3))  # 随机延时，避免请求过于频繁


if __name__ == "__main__":
    settings = get_settings()
    keyword = settings.get('keyword', 'default_keyword')
    download_folder = settings.get('download_folder', 'downloads')
    num_images = settings.get('num_images', 10)
    input_type = settings.get('input_type', 'text')
    image_file = settings.get('image_file', '')

    if input_type == 'text':
        img_urls = baidu_image_search(keyword)
    elif input_type == 'image' and os.path.isfile(image_file):
        img_urls = baidu_image_search_by_image(image_file)
    else:
        logger.error(f"Invalid input type or image file not found.")
        img_urls = []

    if img_urls:
        download_images(img_urls[:num_images], keyword, download_folder)
    else:
        logger.error(f"No image URLs found for {keyword}.")
"""
