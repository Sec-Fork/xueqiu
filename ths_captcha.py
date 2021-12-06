
import os
import time
import random
import requests
import cv2
import numpy as np
from logger import Logger
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BORDER = 6

class Crawler():
    def __init__(self, driver, logname='log/xueqiu.log') -> None:
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)
        self.logger = Logger(filename=logname, level='DEBUG').loggerImp()

    def do_captcha(self, refresh_times=1):
        du = DragUtil(self.driver)

        try:
            self.wait_pic()
            # 获取滑块
            slider = self.get_slider()
            image_bg = self.get_bg_image_by_request('captcha1.png')
            image_font = self.get_font_image_by_request('captcha2.png')
            image_origin_width = self.get_bg_image_width(image_bg)
            image_show_width = self.get_show_image_width()
            # # 获取缺口位置
            gap = self.get_pos_by_match(image_bg, image_font)
            # 按照图片比例计算移动距离
            gap = int(gap*(image_show_width/image_origin_width))
            du.simulateDragX(slider, gap)
            # 判断是否通过验证
            time.sleep(2)
            if self.driver.find_element(By.ID, 'captcha').is_displayed():
                self.logger.error('失败，再来一次，第 {} 次尝试'.format(refresh_times))
                self.do_captcha(refresh_times+1)
            else:
                self.logger.info('认证成功')
                self.closelogger()
        except Exception as e:
            self.logger.error('失败，再来一次，第 {} 次尝试'.format(refresh_times))
            self.logger.error(str(e))
            time.sleep(1)
            self.refresh()
            time.sleep(1)
            self.do_captcha()

    def refresh(self,):
        time.sleep(1)
        self.logger.info('刷新验证码')
        r = self.driver.find_element(By.ID, 'slicaptcha-icon')
        ActionChains(self.driver).move_to_element(r).click(r).perform()

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.ID, 'slider')))
        return slider

    def get_bg_image_width(self, image):
        return image.shape[1]

    def get_show_image_width(self):
        image = self.driver.find_element(By.ID, 'slicaptcha-img')
        return image.size['width']

    def get_bg_image_by_request(self, name='captcha.png'):
        img_src = self.driver.find_element(By.ID, 'slicaptcha-img').get_attribute('src')
        img = requests.get(img_src)
        img = cv2.cvtColor(np.asarray(Image.open(BytesIO(img.content))), cv2.COLOR_RGB2BGR)
        # cv2.imwrite(name, img)
        return img

    def get_font_image_by_request(self, name='captcha.png'):
        img_src = self.driver.find_element(By.ID, 'slicaptcha-block').get_attribute('src')
        img = requests.get(img_src)
        img = cv2.cvtColor(np.asarray(Image.open(BytesIO(img.content))), cv2.COLOR_RGB2BGR)
        # cv2.imwrite(name, img)
        return img

    def get_pos_by_match(self, image_bg, image_font):
        image_bg = cv2.Canny(cv2.GaussianBlur(image_bg, (3, 3), 0), 50, 150)
        image_font = cv2.Canny(cv2.GaussianBlur(image_font, (3, 3), 0), 50, 150)
        res = cv2.matchTemplate(image_font, image_bg, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc[0]  # 横坐标
        self.logger.info('需要移动的距离: {}'.format(top_left))
        return top_left

    def wait_pic(self):
        '''
        等待验证图片加载完成
        :return None
        '''
        self.wait.until(EC.presence_of_element_located((By.ID, 'slicaptcha-img')))

    def closelogger(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def open_captcha(self):
        # self.driver.switch_to.frame(0)
        
        account_login = self.wait.until(EC.presence_of_element_located((By.ID, 'to_account_login')))
        ActionChains(self.driver).move_to_element(account_login).click(account_login).perform()
        self.wait.until(EC.presence_of_element_located((By.ID, 'uname')))
        self.driver.find_element(By.ID, 'uname').send_keys('12342')
        self.driver.find_element(By.ID, 'passwd').send_keys('12342')
        login_btn = self.driver.find_element(By.CLASS_NAME, "submit_btn")
        ActionChains(self.driver).move_to_element(login_btn).click(login_btn).perform()

class DragUtil():
    def __init__(self, driver):
        self.driver = driver

    def __getRadomPauseScondes(self):
        """
        :return:随机的拖动暂停时间
        """
        return random.uniform(0.6, 0.9)

    def simulateDragX(self, source, targetOffsetX, move_action_chains=None):
        """
        模仿人的拖拽动作：快速沿着X轴拖动（存在误差），再暂停，然后修正误差
        防止被检测为机器人，出现“图片被怪物吃掉了”等验证失败的情况
        :param source:要拖拽的html元素
        :param targetOffsetX: 拖拽目标x轴距离
        :return: None
        """
        action_chains = move_action_chains if move_action_chains else webdriver.ActionChains(self.driver)
        # 点击，准备拖拽
        action_chains.click_and_hold(source)
        # 拖动次数，二到三次
        dragCount = random.randint(2, 3)
        if dragCount == 2:
            # 总误差值
            sumOffsetx = random.randint(-15, 15)
            action_chains.move_by_offset(targetOffsetX + sumOffsetx, 0)
            # 暂停一会
            action_chains.pause(self.__getRadomPauseScondes())
            # 修正误差，防止被检测为机器人，出现图片被怪物吃掉了等验证失败的情况
            action_chains.move_by_offset(-sumOffsetx, 0)
        elif dragCount == 3:
            # 总误差值
            sumOffsetx = random.randint(-15, 15)
            action_chains.move_by_offset(targetOffsetX + sumOffsetx, 0)
            # 暂停一会
            action_chains.pause(self.__getRadomPauseScondes())

            # 已修正误差的和
            fixedOffsetX = 0
            # 第一次修正误差
            if sumOffsetx < 0:
                offsetx = random.randint(sumOffsetx, 0)
            else:
                offsetx = random.randint(0, sumOffsetx)

            fixedOffsetX = fixedOffsetX + offsetx
            action_chains.move_by_offset(-offsetx, 0)
            action_chains.pause(self.__getRadomPauseScondes())

            # 最后一次修正误差
            action_chains.move_by_offset(-sumOffsetx + fixedOffsetX, 0)
            action_chains.pause(self.__getRadomPauseScondes())

        else:
            raise Exception("莫不是系统出现了问题？!")

        # 参考action_chains.drag_and_drop_by_offset()
        action_chains.release()
        action_chains.perform()

    def simpleSimulateDragX(self, source, targetOffsetX):
        """
        简单拖拽模仿人的拖拽：快速沿着X轴拖动，直接一步到达正确位置，再暂停一会儿，然后释放拖拽动作
        B站是依据是否有暂停时间来分辨人机的，这个方法适用。
        :param source:
        :param targetOffsetX:
        :return: None
        """

        action_chains = webdriver.ActionChains(self.driver)
        # 点击，准备拖拽
        action_chains.click_and_hold(source)
        action_chains.pause(0.2)
        action_chains.move_by_offset(targetOffsetX, 0)
        action_chains.pause(0.6)
        action_chains.release()
        action_chains.perform()


if __name__=='__main__':

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
        options.add_argument('--hide-scrollbars')
        options.add_argument("disable-blink-features=AutomationControlled")  # 去掉了webdriver痕迹
        options.add_argument(
            'user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"')
        driver = webdriver.Chrome(options=options)
        # driver.maximize_window()

        # 若为此url，则需要切换 frame
        # url = https://www.10jqka.com.cn/index.html
        # driver.get(url)
        # self.driver.switch_to.frame(0)
        
        # 若为此url，则不需要切换 frame
        url = 'https://upass.10jqka.com.cn/login?redir=HTTP_REFERER'
        driver.get(url)

        c = Crawler(driver)
        c.open_captcha()
        c.do_captcha()
        print('第 {} 次尝试成功'.format(i))
        driver.close()
