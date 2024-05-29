# -*- coding: utf-8 -*-

"""
Project Name: Crawler
File Created: 2024.05.28
Author: ZhangYuetao
GitHub: https://github.com/VerySeriousMan/Crawler
File Name: job_process.py
last renew 2024.05.29
"""

import os
import time
import random
import requests
import re
from PyQt5.QtWidgets import QApplication
from bs4 import BeautifulSoup
from logger import logger


class JobProcessor:
    def __init__(self, pic_utils_instance):
        self.pic_utils_instance = pic_utils_instance
        self.terminate = False  # 初始状态为未终止

    def terminate_download(self):
        self.terminate = True

    def baidu_image_search(self, keyword):
        search_url = "https://image.baidu.com/search/index?tn=baiduimage&word="
        headers = {
            "User-Agent": self.pic_utils_instance.get_random_user_agent(),
        }
        params = self.pic_utils_instance.get_params('baidu_text_search_param.json')
        params['queryWord'] = keyword
        params['word'] = keyword

        all_urls = []

        for pn in range(10):
            params['pn'] = str(int(pn + 1) * 30)
            proxy = {'http': self.pic_utils_instance.get_random_proxy()}
            try:
                logger.info(f"Trying proxy: {proxy}")
                response = requests.get(search_url, headers=headers, params=params, proxies=proxy, timeout=10)
                logger.info(f"Response status code: {response.status_code}")
                response.encoding = 'utf-8'
                html = response.text
                img_urls = re.findall('"thumbURL":"(.*?)",', html, re.S)
                logger.info(f"Found image URLs: {img_urls}")
                all_urls.extend(img_urls)

                QApplication.processEvents()  # 防止界面冻结

            except Exception as e:
                logger.error(f"Image search failed with proxy {proxy}: {e}")
                continue

        return all_urls

    def baidu_image_search_by_image(self, image_path):
        upload_url = "https://graph.baidu.com/upload"
        headers = {
            "User-Agent": self.pic_utils_instance.get_random_user_agent(),
        }

        try:
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                proxy = {'http': self.pic_utils_instance.get_random_proxy()}

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

        all_urls = []
        try:
            for pn in range(10):  # Increase range if necessary to get more images
                params = {'pn': str(pn * 30)}
                proxy = {'http': self.pic_utils_instance.get_random_proxy()}

                logger.info(f"Trying proxy: {proxy} for image search page {pn}")
                response = requests.get(img_search_url, headers=headers, params=params, proxies=proxy, timeout=10)
                logger.info(f"Response status code: {response.status_code}")
                response.encoding = 'utf-8'
                html = response.text

                soup = BeautifulSoup(html, "html.parser")
                img_tags = soup.find_all("img")
                img_urls = [img.get("src") for img in img_tags if img.get("src") and "http" in img.get("src")]

                logger.info(f"Found image URLs on page {pn}: {img_urls}")
                all_urls.extend(img_urls)

                # Remove duplicates
                all_urls = list(set(all_urls))

                QApplication.processEvents()
        except Exception as e:
            logger.error(f"Image search failed with proxy {proxy}: {e}")

        return all_urls

    def download_images(self, img_urls, keyword, download_path):
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        for idx, img_url in enumerate(img_urls):
            if self.terminate:  # 如果处于终止状态，则退出下载任务
                logger.info("Download terminated.")
                break

            headers = {
                "User-Agent": self.pic_utils_instance.get_random_user_agent(),
            }
            proxies = self.pic_utils_instance.get_proxies()
            for proxy in proxies:
                try:
                    logger.info(f"Trying proxy: {proxy}")
                    img_data = requests.get(img_url, headers=headers, proxies={"http": proxy}, timeout=10).content
                    logger.info(f"Downloaded image data size: {len(img_data)}")
                    with open(os.path.join(download_path, f"{keyword}_{idx + 1}.jpg"), 'wb') as img_file:
                        img_file.write(img_data)
                    logger.info(f"Downloaded {keyword}_{idx + 1}.jpg")

                    QApplication.processEvents()  # 防止界面冻结

                    break
                except Exception as e:
                    logger.error(f"Failed to download {img_url} with proxy {proxy}: {e}")
                    continue

            time.sleep(random.uniform(1, 3))  # 随机延时，避免请求过于频繁

        if not self.terminate:  # 如果未被终止，则打印下载完成信息
            logger.info(f"Downloaded image finished")
