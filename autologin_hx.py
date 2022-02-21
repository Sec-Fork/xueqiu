#!/usr/bin/python3
# -*- coding: UTF-8 -*-
'''
Author: harry lu
Date: 2022-02-21 23:46:08
LastEditTime: 2022-02-22 00:25:39
LastEditors: harry lu
Description: 自动登录网站
FilePath: \crawler\src\autologin_hx.py
'''

import io
import time
import random

import ddddocr
from io import BytesIO
from PIL import Image
from logger import Logger
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Fxcpiital:
    def __init__(self) -> None:
        self.url = "http://admin.hxcapital.cn/"
        self.ocr = ddddocr.DdddOcr()
        self.init_browser()
        
        

    def init_browser(self):
        """初始化浏览器
        """
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
        caps = {
            'browserName': 'chrome',
            'loggingPrefs': {
                'browser': 'ALL',
                'driver': 'ALL',
                'performance': 'ALL',
            },
            'goog:chromeOptions': {
                'perfLoggingPrefs': {
                'enableNetwork': True,
                },
                'w3c': False, 
            },
            }
        self.browser = webdriver.Chrome(options=options, desired_capabilities=caps)
        self.wait = WebDriverWait(self.browser, 20)

    def autologin(self):
        self.open()
        self.set_information()
        self.login()
        

    def open(self):
        """
        打开网页
        :return: None
        """
        self.browser.get(self.url)

    def __del__(self):
        # self.browser.close()
        pass

    def set_information(self):
        self.browser.find_element(By.NAME, 'username').send_keys('lijun')
        self.browser.find_element(By.NAME, 'password').send_keys('qaz123456')
        self.browser.find_element(By.NAME, 'verifyCode').send_keys(self.get_code())


    def get_code(self):
        self.wait.until(EC.presence_of_element_located((By.ID, 's-canvas')))
        code_ele = self.browser.find_element(By.ID, 's-canvas')
        code_location = code_ele.location
        code_size = code_ele.size
        top, bottom, left, right = code_location['y'], code_location['y'] + code_size['height'], \
            code_location['x'], code_location['x'] + code_size['width']
        screenshot = self.get_screenshot()
        code = screenshot.crop((left, top, right, bottom))
        code.save('123.png')
        imgByteArr = io.BytesIO()
        code.save(imgByteArr, format='PNG')
        res = self.ocr.classification(imgByteArr.getvalue())
        print(res)
        return res

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def login(self):
        r = self.browser.find_element(By.CLASS_NAME, 'login-btn')
        print(r)
        ActionChains(self.browser).move_to_element(r).click(r).perform()

def main():
    fx = Fxcpiital()
    fx.autologin()

if __name__=="__main__":
    main()