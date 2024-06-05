# -*- coding: utf-8 -*-

"""
Project Name: Crawler
File Created: 2024.05.28
Author: ZhangYuetao
GitHub: https://github.com/VerySeriousMan/Crawler
File Name: job_process.py
last renew 2024.06.04
"""

import os
import json
import time
import random
import requests
import re
from PyQt5.QtWidgets import QApplication
from bs4 import BeautifulSoup
from logger import logger
from utils import pic_utils


class JobProcessor:
    def __init__(self, pic_utils_instance):
        self.pic_utils_instance = pic_utils_instance
        self.terminate = False  # 初始状态为未终止
        self.time_settings_path = 'setting/time_settings.toml'
        self.pic_utils_instance = pic_utils()

    def terminate_download(self):
        self.terminate = True

    def so_image_search(self, keyword, n):
        headers = {
            "User-Agent": self.pic_utils_instance.get_random_user_agent(),
        }
        all_urls = []

        for pn in range(n):
            if self.terminate:  # 如果处于终止状态，则退出获取任务
                logger.info("Get url terminated.")
                break
            search_url = f"https://image.so.com/i?q={keyword}&sn={pn * 30}"
            proxy = {'http': self.pic_utils_instance.get_random_proxy()}

            try:
                logger.info(f"Trying proxy: {proxy}")
                response = requests.get(search_url, headers=headers, proxies=proxy, timeout=10)
                logger.info(f"Response status code: {response.status_code}")
                response.encoding = 'utf-8'
                html = response.text
                img_urls_str = re.findall('"thumb":"(.*?)",', html, re.S)
                # 解析转义字符的URL
                img_urls = [url.replace('\\/', '/') for url in img_urls_str]
                logger.info(f"Found image URLs: {img_urls}")
                all_urls.extend(img_urls)

                QApplication.processEvents()  # 防止界面冻结

            except Exception as e:
                logger.error(f"Image search failed with proxy {proxy}: {e}")
                continue

            return all_urls

    def sogou_image_search(self, keyword, n):
        headers = {
            "User-Agent": self.pic_utils_instance.get_random_user_agent(),
        }
        all_urls = []

        search_url = f"https://pic.sogou.com/pics?"

        params = self.pic_utils_instance.get_params('sogou_text_search_param.json')
        params['query'] = keyword

        for pn in range(n):
            if self.terminate:  # 如果处于终止状态，则退出获取任务
                logger.info("Get url terminated.")
                break

            proxy = {'http': self.pic_utils_instance.get_random_proxy()}
            params['start'] = pn * 48

            try:
                logger.info(f"Trying proxy: {proxy}")
                response = requests.get(search_url, headers=headers, params=params, proxies=proxy, timeout=10)
                logger.info(f"Response status code: {response.status_code}")
                response.encoding = 'utf-8'
                html = response.text
                img_urls_str = re.findall('"picUrl":"(.*?)",', html, re.S)
                # 解析转义字符的URL
                img_urls = [json.loads('"' + url + '"') for url in img_urls_str]
                logger.info(f"Found image URLs: {img_urls}")
                all_urls.extend(img_urls)

                QApplication.processEvents()  # 防止界面冻结

            except Exception as e:
                logger.error(f"Image search failed with proxy {proxy}: {e}")
                continue

        return all_urls

    def bing_image_search(self, keyword, n):
        headers = {
            "User-Agent": self.pic_utils_instance.get_random_user_agent(),
        }
        all_urls = []

        for pn in range(n):
            if self.terminate:  # 如果处于终止状态，则退出获取任务
                logger.info("Get url terminated.")
                break
            search_url = f"https://www.bing.com/images/search?q={keyword}&first={pn * 35 + 1}&count=35"
            proxy = {'http': self.pic_utils_instance.get_random_proxy()}

            try:
                logger.info(f"Trying proxy: {proxy}")
                response = requests.get(search_url, headers=headers, proxies=proxy, timeout=10)
                logger.info(f"Response status code: {response.status_code}")
                soup = BeautifulSoup(response.text, 'html.parser')

                # 通过class选择器找到所有图片链接
                image_links = soup.find_all('a', class_='iusc')

                # 提取图片链接
                urls = []
                for link in image_links:
                    m = link.attrs.get('m')
                    if m:
                        m_json = json.loads(m)
                        if 'murl' in m_json:
                            urls.append(m_json['murl'])
                logger.info(f"Found image URLs: {urls}")
                all_urls.extend(urls)

                QApplication.processEvents()  # 防止界面冻结

            except Exception as e:
                logger.error(f"Image search failed with proxy {proxy}: {e}")
                continue

        return all_urls

    def baidu_image_search(self, keyword, n):
        search_url = "https://image.baidu.com/search/index?tn=baiduimage&word="
        headers = {
            "User-Agent": self.pic_utils_instance.get_random_user_agent(),
        }
        params = self.pic_utils_instance.get_params('baidu_text_search_param.json')
        params['queryWord'] = keyword
        params['word'] = keyword

        all_urls = []

        for pn in range(n):
            if self.terminate:  # 如果处于终止状态，则退出获取任务
                logger.info("Get url terminated.")
                break

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

    # def baidu_image_search_by_image(self, image_path):
    #     upload_url = "https://graph.baidu.com/upload"
    #     headers = {
    #         "User-Agent": self.pic_utils_instance.get_random_user_agent(),
    #     }
    #
    #     try:
    #         with open(image_path, 'rb') as image_file:
    #             files = {'image': image_file}
    #             proxy = {'http': self.pic_utils_instance.get_random_proxy()}
    #
    #             logger.info(f"Trying proxy: {proxy} for image upload")
    #             response = requests.post(upload_url, headers=headers, files=files, proxies=proxy, timeout=10)
    #             logger.info(f"Response status code for upload: {response.status_code}")
    #             response_data = response.json()
    #             logger.info(f"Response data for upload: {response_data}")
    #
    #             if response_data.get('status') != 0:
    #                 logger.error(f"Image upload failed with error: {response_data.get('msg')}")
    #                 return []
    #
    #             img_search_url = response_data['data']['url']
    #             logger.info(f"Uploaded image search URL: {img_search_url}")
    #     except Exception as e:
    #         logger.error(f"Image upload failed with proxy {proxy}: {e}")
    #         return []
    #
    #     all_urls = []
    #     try:
    #         for pn in range(10):  # Increase range if necessary to get more images
    #             params = {'pn': str(pn * 30)}
    #             proxy = {'http': self.pic_utils_instance.get_random_proxy()}
    #
    #             logger.info(f"Trying proxy: {proxy} for image search page {pn}")
    #             response = requests.get(img_search_url, headers=headers, params=params, proxies=proxy, timeout=10)
    #             logger.info(f"Response status code: {response.status_code}")
    #             response.encoding = 'utf-8'
    #             html = response.text
    #
    #             soup = BeautifulSoup(html, "html.parser")
    #             img_tags = soup.find_all("img")
    #             img_urls = [img.get("src") for img in img_tags if img.get("src") and "http" in img.get("src")]
    #
    #             logger.info(f"Found image URLs on page {pn}: {img_urls}")
    #             all_urls.extend(img_urls)
    #
    #             # Remove duplicates
    #             all_urls = list(set(all_urls))
    #
    #             QApplication.processEvents()
    #     except Exception as e:
    #         logger.error(f"Image search failed with proxy {proxy}: {e}")
    #
    #     return all_urls

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

            try_times = 0

            for proxy in proxies:
                try_times = try_times + 1
                if try_times < 3:
                    try:
                        logger.info(f"Trying proxy: {proxy}")
                        img_data = requests.get(img_url, headers=headers, proxies={"http": proxy}, timeout=10).content
                        logger.info(f"Downloaded image data size: {len(img_data)}")
                        if len(img_data) > 1024:
                            with open(os.path.join(download_path, f"{keyword}_{idx + 1}.jpg"), 'wb') as img_file:
                                img_file.write(img_data)
                            logger.info(f"Downloaded {keyword}_{idx + 1}.jpg")

                        else:
                            logger.warning(f"{keyword}_{idx + 1}.jpg size does not match, do not download")

                        QApplication.processEvents()  # 防止界面冻结

                        break
                    except Exception as e:
                        logger.error(f"Failed to download {img_url} with proxy {proxy}: {e}")
                        continue

            time_settings = self.pic_utils_instance.get_settings(self.time_settings_path)
            min_download_time = time_settings.get('min_download_time', 0.2)
            max_download_time = time_settings.get('max_download_time', 0.6)
            time.sleep(random.uniform(min_download_time, max_download_time))  # 随机延时，避免请求过于频繁

        if not self.terminate:  # 如果未被终止，则打印下载完成信息
            logger.info(f"Downloaded image finished")
