# -*- coding: utf-8 -*-

"""
Project Name: Crawler
File Created: 2024.05.29
Author: ZhangYuetao
File Name: get_proxy.py
Update: 2024.05.30
"""

import os
import requests
from bs4 import BeautifulSoup
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_zdaye_proxies(num_pages=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    base_url = "https://www.zdaye.com/free"

    all_proxies = []

    for page in range(1, num_pages + 1):
        url = f"{base_url}/{page}/"
        try:
            logger.info(f"Fetching proxies from {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")

            # 根据网页结构，找到包含IP的表格
            proxy_table = soup.find("table", attrs={"id": "ipc"})
            if not proxy_table:
                logger.error("Proxy table not found on page {page}.")
                continue

            # 提取表格中的所有行
            rows = proxy_table.find_all("tr")

            # 跳过表头，从第二行开始
            proxies = []
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) > 1:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    proxies.append(f"{ip}:{port}")

            logger.info(f"Found proxies on page {page}: {proxies}")
            all_proxies.extend(proxies)
        except Exception as e:
            logger.error(f"Failed to fetch proxies from {url}: {e}")
            continue

    return all_proxies


def get_docip_proxies():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    url = "https://www.docip.net/free"

    try:
        logger.info(f"Fetching proxies from {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        # 找到包含IP信息的表格行
        proxy_rows = soup.find_all("tr", class_="bg-white border-b dark:bg-gray-800 dark:border-gray-700")

        proxies = []
        for row in proxy_rows:
            # 提取表格行中第一个表格单元格中的IP地址和端口号
            ip_port_cell = row.find("th")
            if ip_port_cell:
                ip_port = ip_port_cell.text.strip()
                proxies.append(f"http://{ip_port}")

        logger.info(f"Found proxies: {proxies}")
        return proxies
    except Exception as e:
        logger.error(f"Failed to fetch proxies from {url}: {e}")
        return []


def save_proxies_to_file(proxies, file_path):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            for proxy in proxies:
                file.write(f"{proxy}\n")
        logger.info(f"Proxies saved to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save proxies to file: {e}")
