# Crawler

Crawl Baidu pictures

## 作者

- **Author**: Zhang Yuetao
- **GitHub**: [VerySeriousMan](https://github.com/VerySeriousMan)


## 项目简介

Crawler 是一个用于抓取百度图片的工具。该工具提供了一个简单易用的图形用户界面（GUI），用户可以通过输入关键词，指定下载数量和保存位置，快速地下载百度图片搜索结果。


## 功能介绍

- **关键词搜索**: 通过输入关键词，从百度图片搜索中获取相关图片。
- **数量限制**: 用户可以指定要下载的图片数量。
- **保存位置**: 用户可以选择图片下载保存的文件夹。
- **日志记录**: 实时显示下载过程中的日志信息，包括下载进度、错误信息等，且日志信息不同级别显示不同颜色，便于查看。


## 反爬机制

为了应对反爬机制，我们实现了以下措施：

- **随机延时**: 在发送请求时，随机延时一段时间，以模拟人类操作，降低被封禁的风险。
- **用户代理池**: 使用多个随机的用户代理（User-Agent）来发送请求，减少被识别为机器人的概率。
- **代理 IP 池**: 使用多个随机的代理 IP 地址来发送请求，防止 IP 被封禁。


## 环境依赖

- Python 3.x
- PyQt5
- qt_material
- requests
- colorlog


## 安装

1. 克隆项目到本地：

   ```bash
   git clone https://github.com/VerySeriousMan/Crawler.git
   
2. 安装依赖包：

   ```bash
   pip install -r requirements.txt


## 使用方法

1. 进入项目目录，运行主程序：

   ```bash
   python main.py
   
2. 在打开的图形用户界面中，输入关键词，指定下载数量和保存位置，然后点击提交按钮开始下载。


## 贡献
如果你有好的建议或发现了问题，欢迎提交 issue 或 pull request。