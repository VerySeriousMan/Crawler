# -*- coding: utf-8 -*-

"""
Project Name: Crawler
File Created: 2024.05.24
Author: ZhangYuetao
File Name: utils.py
Update: 2024.06.04
"""

import os
import random
import json
import toml
import chardet
from logger import logger
from get_proxy import get_zdaye_proxies, save_proxies_to_file, get_docip_proxies


class pic_utils:
    def __init__(self):
        self.user_agents_path = 'lake/user_agents.txt'
        self.proxies_path = 'lake/proxies.txt'
        self.param_dir = 'setting/param'
        self.settings_path = 'setting/settings.toml'
        self.web_dir = 'setting/web_list.txt'

    def get_user_agents(self):
        try:
            with open(self.user_agents_path, "r", encoding='utf-8') as file:
                user_agents = [line.strip() for line in file if line.strip()]
            return user_agents
        except FileNotFoundError:
            logger.error("User-Agent file not found.")
            return []

    def get_random_user_agent(self):
        user_agents = self.get_user_agents()
        return random.choice(user_agents) if user_agents else None

    def get_proxies(self):
        try:
            with open(self.proxies_path, "r", encoding='utf-8') as file:
                proxies = [line.strip() for line in file if line.strip()]
            return proxies
        except FileNotFoundError:
            logger.error("Proxies file not found.")
            return []

    def get_random_proxy(self):
        proxies = self.get_proxies()
        return random.choice(proxies) if proxies else None

    def get_params(self, params_name):
        try:
            with open(os.path.join(self.param_dir, params_name), "r", encoding='utf-8') as file:
                params = json.load(file)
            return params
        except FileNotFoundError:
            logger.error("Params file not found.")
            return {}
        except json.JSONDecodeError:
            logger.error("Error decoding params file.")
            return {}

    def get_settings(self, settings_path):
        try:
            with open(settings_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']

            with open(settings_path, 'r', encoding=encoding) as f:
                settings = toml.load(f)
            return settings
        except FileNotFoundError:
            logger.error("Settings file not found.")
            return {}
        except toml.TomlDecodeError:
            logger.error("Error decoding settings file.")
            return {}
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error: {e}")
            return {}

    def refresh_settings(self, keyword, download_folder, num_images, input_type, image_file):
        settings = self.get_settings(self.settings_path)

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

        try:
            with open(self.settings_path, "w", encoding='utf-8') as file:
                toml.dump(settings, file)
            logger.info("Settings updated successfully.")
        except Exception as e:
            logger.error(f"Failed to update settings: {e}")

    def refresh_proxies(self):
        proxies_zdaye = get_zdaye_proxies(5)
        proxies_docip = get_docip_proxies()
        all_proxies = [proxies_zdaye]
        all_proxies.extend(proxies_docip)
        if all_proxies is not None and all_proxies != []:
            save_proxies_to_file(all_proxies, self.proxies_path)
        else:
            logger.warning("Failed to update proxies.")
