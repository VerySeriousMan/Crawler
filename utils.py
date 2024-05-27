# -*- coding: utf-8 -*-

"""
Project Name: Crawler
File Created: 2024.05.24
Author: ZhangYuetao
GitHub: https://github.com/VerySeriousMan/Crawler
File Name: utils.py
last renew 2024.05.27
"""

import re
import requests
import os
import time
import random
import json
import toml
from bs4 import BeautifulSoup
from logger import logger


class pic_utils:
    def __init__(self):
        self.user_agents_path = 'lake/user_agents.txt'
        self.proxies_path = 'lake/proxies.txt'
        self.param_path = 'setting/param.json'
        self.settings_path = 'setting/settings.toml'

    def get_user_agents(self):
        try:
            with open(self.user_agents_path, "r") as file:
                user_agents = [line.strip() for line in file if line.strip()]
            return user_agents
        except FileNotFoundError:
            logger.error("User-Agent file not found.")
            return []

    def get_random_user_agent(self):
        user_agents = self.get_user_agents()
        return random.choice(user_agents) if user_agents else None

    # 从文件中读取代理列表
    def get_proxies(self):
        try:
            with open(self.proxies_path, "r") as file:
                proxies = [line.strip() for line in file if line.strip()]
            return proxies
        except FileNotFoundError:
            logger.error("Proxies file not found.")
            return []

    def get_random_proxy(self):
        proxies = self.get_proxies()
        return random.choice(proxies) if proxies else None

    # 从文件中读取查询参数
    def get_params(self):
        try:
            with open(self.param_path, "r") as file:
                params = json.load(file)
            return params
        except FileNotFoundError:
            logger.error("Params file not found.")
            return {}
        except json.JSONDecodeError:
            logger.error("Error decoding params file.")
            return {}

    # 从 settings.toml 文件中读取设置
    def get_settings(self):
        try:
            with open(self.settings_path, "r") as file:
                settings = toml.load(file)
            return settings
        except FileNotFoundError:
            logger.error("Settings file not found.")
            return {}
        except toml.TomlDecodeError:
            logger.error("Error decoding settings file.")
            return {}

    def refresh_settings(self, keyword, download_folder, num_images, input_type, image_file):
        settings = self.get_settings()

        # 更新不为空的参数
        if keyword is not None and keyword != '':
            settings['keyword'] = keyword
        if download_folder is not None and download_folder != '':
            settings['download_folder'] = download_folder
        if num_images is not None and num_images != '':
            settings['num_images'] = int(num_images)
        if input_type is not None and input_type != '':
            settings['input_type'] = input_type
        if image_file is not None and image_file != '':
            settings['image_file'] = image_file

        # 将更新后的设置写回到文件中
        try:
            with open(self.settings_path, "w") as file:
                toml.dump(settings, file)
            logger.info("Settings updated successfully.")
        except Exception as e:
            logger.error(f"Failed to update settings: {e}")

    # 在百度图片中搜索图片
    def baidu_image_search(self, keyword):
        search_url = "https://image.baidu.com/search/index?tn=baiduimage&word="
        headers = {
            "User-Agent": self.get_random_user_agent(),
        }
        params = self.get_params()
        params['queryWord'] = keyword
        params['word'] = keyword

        print(params)

        all_urls = []

        for pn in range(10):
            params['pn'] = str(int(pn + 1) * 30)
            proxy = {'http': self.get_random_proxy()}
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

    # 以图搜图功能，开发中。。。
    def baidu_image_search_by_image(self, image_path):
        upload_url = "https://graph.baidu.com/upload"
        headers = {
            "User-Agent": self.get_random_user_agent(),
        }

        # 上传图片获取图片 URL
        try:
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                proxy = {'http': self.get_random_proxy()}

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
    def download_images(self, img_urls, keyword, download_path):
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        for idx, img_url in enumerate(img_urls):
            headers = {
                "User-Agent": self.get_random_user_agent(),
            }
            proxies = self.get_proxies()
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

        logger.info(f"Downloaded image finished")


pu = pic_utils()
