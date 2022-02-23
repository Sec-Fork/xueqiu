#!/usr/bin/python3
# -*- coding: UTF-8 -*-
'''
Author: harry lu
Date: 2022-02-21 23:46:08
LastEditTime: 2022-02-23 10:10:02
LastEditors: harry lu
Description: 自动登录网站
FilePath: /xueqiu/autologin_hx.py
'''

import io
import time
import random
from io import BytesIO

import ddddocr
from loguru import logger
from PIL import Image
# from logger import Logger
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
        self.ocr = ddddocr.DdddOcr(show_ad=False)
        self.verifyCode_times = 10 # 验证码判断失败次数
        self.chrome_exec_path = "./chromedriver" # chromedriver 路径
        self.wait_driver_time = 5 # 等待网页元素时间

        self.init_browser()
        logger.add("autologin_hx.log") # 初始化日志保存位置

    def init_browser(self):
        """初始化浏览器设置
        """
        logger.info("正在初始化浏览器")
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
        
        self.browser = webdriver.Chrome(executable_path=self.chrome_exec_path,options=options, desired_capabilities=caps)
        self.browser.maximize_window() # 最大化浏览器
        self.wait = WebDriverWait(self.browser, self.wait_driver_time)
        logger.info("浏览器初始化成功")

    def autologin(self, username='lijun', passwd='qaz123456'):
        """
        执行自动登录操作, 一直循环直到登录成功
        """
        try:
            while True:
                self.open()
                self.set_information(username, passwd)
                self.login()
                if self.is_login_success():
                    logger.info("登录成功")
                    break
                logger.info("登录失败")
                time.sleep(2)
        except Exception as e:
            logger.error(str(e))
        time.sleep(100) # 暂停

    def open(self):
        """
        打开网页
        :return: None
        """
        self.browser.get(self.url)

    def __del__(self):
        self.browser.close()
        pass

    def set_information(self, username, passwd):
        """
        填入用户名和密码和验证码
        """
        self.wait.until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(username)
        self.wait.until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(passwd)
        self.wait.until(EC.presence_of_element_located((By.NAME, 'verifyCode'))).send_keys(self.get_code())


    def get_code(self):
        """
        获取图片验证码结果，共判断十次
        """
        i = self.verifyCode_times
        while (i):
            i = i-1
            self.wait.until(EC.presence_of_element_located((By.ID, 's-canvas')))
            code_ele = self.browser.find_element(By.ID, 's-canvas')
            code_location = code_ele.location
            code_size = code_ele.size
            top, bottom, left, right = code_location['y'], code_location['y'] + code_size['height'], \
                code_location['x'], code_location['x'] + code_size['width']
            screenshot = self.get_screenshot()
            code = screenshot.crop((left, top, right, bottom)) # 截取验证码图片
            # code.save('hx_code.png')
            imgByteArr = io.BytesIO()
            code.save(imgByteArr, format='PNG')
            res = self.ocr.classification(imgByteArr.getvalue())
            if len(res) != 4:
                self.refresh_code()
            # res = res + '1'
            return res
        logger.info("验证码识别失败")
        return '0000'

    def refresh_code(self):
        """
        刷新验证码
        """
        code_ele = self.browser.find_element(By.ID, 's-canvas')
        ActionChains(self.browser).move_to_element(code_ele).click(code_ele).perform()
        time.sleep(2)

    def is_login_success(self):
        """
        判断是否登录成功
        若未出现
        """
        try:
            error_message = WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'el-message--error')))
            if error_message:
                return False
            return True
        except Exception as e:
            try:
                em_form = WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'el-form-item__error')))
                if em_form:
                    return False
                return True
            except Exception as e:
                return True
            return True


    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def login(self):
        """
        点击登录按钮
        """
        r = self.browser.find_element(By.CLASS_NAME, 'login-btn')
        ActionChains(self.browser).move_to_element(r).click(r).perform()

def main():
    fx = Fxcpiital()
    fx.autologin()

if __name__=="__main__":
    main()