from tkinter.constants import X
from selenium import webdriver
from time import sleep
import pandas as pd
import random
import datetime
import json
from traceback import print_exc
import os
from xueqiu_captcha import Crawler as XC


def mark_cookies(code):  # 获取登录记录
    global driver
    cookies = driver.get_cookies()
    with open("雪球登录记录/cookies%s.txt"%code, "w") as fp:
        json.dump(cookies, fp)

url='https://xueqiu.com/'
df_zhanghao=pd.read_excel('雪球账号.xlsx')
df_zhanghao=df_zhanghao[df_zhanghao['屏蔽']=='否']
dirs=os.listdir("雪球登录记录")
print(dirs)

for (zhanghao,mima) in zip(df_zhanghao['账号'],df_zhanghao['密码']):
    login=False
    for cks in dirs:
        if str(zhanghao) in cks:
            login=True
    if login==True:
        continue
    try:
        print('-'*30)
        print('开始刷新登录信息：',zhanghao,mima)
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
        driver = webdriver.Chrome(executable_path=r'chromedriver', options=options)
        xc = XC(driver)

        driver.set_page_load_timeout(10)
        driver.get(url)
        sleep(random.uniform(1, 1.5))
        # driver.maximize_window()
        sleep(random.uniform(0.5,1))
        driver.find_element_by_xpath('//*[@id="app"]/nav/div[1]/div[2]/div/div/span').click()
        sleep(random.uniform(0.5, 1))

        ele1=driver.find_element_by_xpath('//*[@name="username"]').send_keys(str(int(zhanghao)))
        driver.find_element_by_xpath('//*[@name="password"]').send_keys(str(mima))
        sleep(random.uniform(0.5,1))
        driver.find_element_by_xpath("//*[text()='登    录']").click()
        sleep(random.uniform(0.5,1))
        try:
            # 点击弹窗广告
            id = driver.find_element_by_class_name('user-name').text
            print(id)
        except:
            print('请滑动滑块手动登录并回车：')
            sleep(random.uniform(2, 3))
            xc.do_captcha()
            # id = driver.find_element_by_class_name('user-name').text
            print(id)
        mark_cookies(zhanghao)
        driver.quit()
        print('保存成功：登录信息已录入，发帖可免登录')
    except Exception as e:
        print(e)
        print('刷新信息有误，已跳过：',zhanghao)