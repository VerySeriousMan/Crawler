# -*- coding: utf-8 -*-

"""
Project Name: Crawler
File Created: 2024.05.23
Author: ZhangYuetao
File Name: main.py
last renew 2024.05.24
"""

import re
import requests
import os
import time
import random
import json
import toml
from bs4 import BeautifulSoup
from io import BytesIO


# 从文件中读取 User-Agent 列表
def get_user_agents():
    with open("lake/user_agents.txt", "r") as file:
        user_agents = [line.strip() for line in file if line.strip()]
    return user_agents


def get_random_user_agent():
    user_agents = get_user_agents()
    return random.choice(user_agents)


# 从文件中读取代理列表
def get_proxies():
    with open("lake/proxies.txt", "r") as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies


def get_random_proxy():
    proxies = get_proxies()
    return random.choice(proxies)


# 从文件中读取查询参数
def get_params():
    with open("setting/param.json", "r") as file:
        params = json.load(file)
    return params


# 从 settings.toml 文件中读取设置
def get_settings():
    with open("setting/settings.toml", "r") as file:
        settings = toml.load(file)
    return settings


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
            print(f"Trying proxy: {proxy}")
            response = requests.get(search_url, headers=headers, params=params, proxies=proxy, timeout=10)
            print("Response status code:", response.status_code)
            response.encoding = 'utf-8'
            html = response.text
            img_urls = re.findall('"thumbURL":"(.*?)",', html, re.S)
            print("Found image URLs:", img_urls)
            all_urls.extend(img_urls)
        except Exception as e:
            print(f"Image search failed with proxy {proxy}: {e}")
            continue

    return all_urls


def baidu_image_search_by_image(image_path):
    upload_url = "https://graph.baidu.com/upload"

    headers = {
        "User-Agent": get_random_user_agent(),
    }

    # 上传图片获取图片 URL
    files = {'image': open(image_path, 'rb')}
    proxy = {'http': get_random_proxy()}

    try:
        print(f"Trying proxy: {proxy} for image upload")
        response = requests.post(upload_url, headers=headers, files=files, proxies=proxy, timeout=10)
        print("Response status code for upload:", response.status_code)
        response_data = response.json()
        print("Response data for upload:", response_data)
        if response_data.get('status') != 0:
            print("Image upload failed with error:", response_data.get('msg'))
            return []
        img_search_url = response_data['data']['url']
        print("Uploaded image search URL:", img_search_url)
    except Exception as e:
        print(f"Image upload failed with proxy {proxy}: {e}")
        return []

    all_urls = []

    try:
        print(f"Trying proxy: {proxy} for image search")
        # 使用代理获取网页内容
        response = requests.get(img_search_url, headers=headers, proxies=proxy, timeout=10)
        print("Response status code:", response.status_code)
        response.encoding = 'utf-8'
        html = response.text

        # 使用 BeautifulSoup 解析 HTML 页面
        soup = BeautifulSoup(html, "html.parser")

        # 查找所有图片标签
        img_tags = soup.find_all("img")

        # 提取图片链接
        img_urls = [img.get("src") for img in img_tags]

        # 过滤掉空链接和非 HTTP/HTTPS 链接
        img_urls = [url for url in img_urls if url and url.startswith(('http://', 'https://'))]

        print("Found image URLs:", img_urls)
        all_urls.extend(img_urls)
    except Exception as e:
        print(f"Image search failed with proxy {proxy}: {e}")

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
                print(f"Trying proxy: {proxy}")
                img_data = requests.get(img_url, headers=headers, proxies={"http": proxy}, timeout=10).content
                print("Downloaded image data size:", len(img_data))
                with open(os.path.join(download_path, f"{keyword}_{idx + 1}.jpg"), 'wb') as img_file:
                    img_file.write(img_data)
                print(f"Downloaded {keyword}_{idx + 1}.jpg")
                break
            except Exception as e:
                print(f"Failed to download {img_url} with proxy {proxy}: {e}")
                continue

        time.sleep(random.uniform(1, 3))  # 随机延时，避免请求过于频繁


if __name__ == "__main__":
    settings = get_settings()
    keyword = settings['keyword']
    download_folder = settings['download_folder']
    num_images = settings['num_images']
    input_type = settings['input_type']
    image_file = settings['image_file']

    if input_type == 'text':
        img_urls = baidu_image_search(keyword)
    elif input_type == 'image' and os.path.isfile(image_file):
        img_urls = baidu_image_search_by_image(image_file)
        print('222')
    else:
        print(f"Invalid input type or image file not found.")
        img_urls = []

    if img_urls:
        download_images(img_urls[:num_images], keyword, download_folder)
    else:
        print(f"No image URLs found for {keyword}.")
