

import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from xueqiu_captcha import Crawler as XC

for i in range(1,11):

    print('第 {} 次尝试'.format(i))

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
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"')
    # driver = webdriver.Chrome(executable_path=r'chromedriver', options=options)
    driver = webdriver.Chrome(executable_path=r'chromedriver',service_args=['hide_console' ,], options=options)

    driver.set_page_load_timeout(10)
    driver.get('https://xueqiu.com/')
    sleep(random.uniform(1, 2))
    # driver.maximize_window()
    sleep(5)

    ele_login_id = driver.find_element_by_xpath('//*[@id="app"]/nav/div[1]/div[2]/div/div/span')
    driver.execute_script("arguments[0].click();", ele_login_id)


    sleep(random.uniform(1, 2))

    ele1 = driver.find_element_by_xpath('//*[@name="username"]').send_keys("17620135651")
    # ele1 = driver.find_element_by_xpath('//*[@name="username"]').send_keys("176201356"+ str(random.randint(1,9))+ str(random.randint(1,9)))
    driver.find_element_by_xpath('//*[@name="password"]').send_keys("123456")

    while(True):

        elem_login = WebDriverWait(driver, 5, 1).until(EC.presence_of_element_located((By.XPATH, "//*[text()='登    录']")))
        sleep(random.uniform(0.4, 2))
        elem_login.click()

        try:
            driver.find_element_by_class_name("geetest_panel_success")
            print("点击登录成功")
            break
        except:
            print("点击登录失败,重试中。。。")

    sleep(random.uniform(2, 2))


    xc = XC(driver)
    xc.do_captcha()
    print('第 {} 次尝试成功'.format(i))
    driver.close()



