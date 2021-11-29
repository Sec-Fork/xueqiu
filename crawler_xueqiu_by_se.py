#!/usr/bin/python3
# -*- coding: UTF-8 -*-
'''
Author: harry lu
Date: 2021-11-26 23:00:11
LastEditTime: 2021-11-26 23:18:29
LastEditors: harry lu
Description: 
FilePath: \crawler\crawler_xueqiu_by_se.py
'''

import requests
from bs4 import BeautifulSoup
import sys

import time
import random
from io import BytesIO
from PIL import Image
import pandas
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from xlrd import open_workbook
from xlutils.copy import copy

class Crawler():
    def __init__(self) -> None:
        self.url = 'https://xueqiu.com/'
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('–log-level=3')
        options.add_argument('--incognito')  # 隐身模式启动
        options.add_argument('disable-infobars')  # 隐藏提示语：Chrome正在受到自动软件的控制
        options.add_argument('lang=zh_CN.UTF-8')  # 设置中文
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        # options.add_argument('--user-data-dir=/dev/null')  # Start with a clean profile
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--disable-gpu')
        options.add_argument("disable-blink-features=AutomationControlled")  # 去掉了webdriver痕迹
        options.add_argument(
            'user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"')
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 20)
        self.browser.get(self.url)
        self.urls=[]

    def find_articles(self):
        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'AnonymousHome_a__placeholder_3RZ')))
        class_='AnonymousHome_a__placeholder_3RZ'
        articles = self.browser.find_elements(By.CLASS_NAME, class_)

        for a in articles:
            # print(a.get_attribute("href"))
            url = a.get_attribute("href")
            if url not in self.urls:
                self._get_article_content(url)
            self.urls.append(url)
        
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)
        self._find_more()
        self.find_articles()

    def _find_more(self):
        try:
            more = self.browser.find_element(By.CLASS_NAME, 'AnonymousHome_home__timeline__more_6RI')
            ActionChains(self.browser).move_to_element(more).click(more).perform()
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(1)
        except:
            pass

    def _get_article_content(self, url):
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            'elastic-apm-traceparent': '00-201e84f5374b4fe259d460b0023d2643-39d10f8d0c29018f-01',
            'Host': 'xueqiu.com',
            'Referer': 'https://xueqiu.com/',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            }

        base_content = requests.get(url, headers=headers)
        if base_content.encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(base_content.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = base_content.apparent_encoding
            # encode_content = req.content.decode(encoding, 'replace').encode('utf-8', 'replace')
            # global encode_content
            base_content = base_content.content.decode(encoding, 'replace') #如果设置为replace，则会用?取代非法字符；

        bs = BeautifulSoup(base_content.text, 'lxml')

        source = ''
        edit_time = ''

        display_name = bs.find(class_='avatar__name').a['data-screenname']

        title = ''
        if bs.find(class_='article__bd__title'):
            title = bs.find(class_='article__bd__title').get_text()
        else:
            title = bs.title.get_text()

        edit_time_bs = bs.find(class_='edit-time')
        if edit_time_bs:
            edit_time = edit_time_bs.get_text()
        elif bs.find(class_='time'):
            edit_time = bs.find(class_='time').get_text()
        source_bs = bs.find(class_='source').a
        if source_bs:
            source = source_bs.get_text()
        
        content = bs.find(class_='article__bd__detail').get_text()



        print('-'*15)
        # print(url)
        print(display_name)
        # print(title)
        # print(source)
        # print(edit_time)
        # print(content)

        self.save(title=title, display_name=display_name, edit_time=edit_time, source=source, content=content)

    def save(self, **kwags):
        excel = open_workbook('xueqiu.xls')
        rows = excel.sheets()[0].nrows
        excel = copy(excel)
        table = excel.get_sheet(0)

        row = rows

        table.write(row, 0, kwags['title'])
        table.write(row, 1, kwags['display_name'])
        table.write(row, 2, kwags['edit_time'])
        table.write(row, 3, kwags['source'])
        table.write(row, 4, kwags['content'])

        excel.save("xueqiu.xls")


def main():
    crawler = Crawler()
    urls = crawler.find_articles()


if __name__=='__main__':
    main()

