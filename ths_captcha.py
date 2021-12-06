
import os
import time
import random
import requests
import cv2
import numpy as np
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
    def __init__(self, driver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)
        self.window_size = None
        self.client_width = 0
        self.client_height = 0

    def do_captcha(self, refresh_times=1):
        du = DragUtil(self.driver)

        try:
            time.sleep(2)
            # 获取滑块
            slider = self.get_slider()
            image_bg = self.get_bg_image_by_request('captcha1.png')
            image_font = self.get_font_image_by_request('captcha2.png')
            # # 获取缺口位置
            gap = self.get_pos_by_match(image_bg, image_font)
            gap = int(gap*(280/340))
            du.simulateDragX(slider, gap)
            # 判断是否通过验证
            time.sleep(2)
            if self.driver.find_element(By.ID, 'captcha').is_displayed():
                print('失败，再来一次，第 {} 次尝试'.format(refresh_times))
                self.do_captcha(refresh_times+1)
            else:
                print('认证成功')
        except Exception as e:
            print('失败，再来一次，第 {} 次尝试'.format(refresh_times))
            print(e)
            time.sleep(1)
            self.refresh()
            time.sleep(1)
            self.do_captcha()

    def refresh(self,):
        time.sleep(1)
        r = self.driver.find_element(By.ID, 'slicaptcha-icon')
        ActionChains(self.driver).move_to_element(r).click(r).perform()

    def get_geetest_button(self):
        """
        获取初始验证按钮
        :return:
        """
        # 验证按钮
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
        return button

    def move_to_right(self, slider, move_action_chains):
        move_action_chains.click_and_hold(slider)
        offset = self.driver.find_element(By.ID, 'slicaptcha-container').size['width']
        print('width: ', offset)
        time.sleep(1)
        move_action_chains.move_by_offset(offset-54, 0)
        move_action_chains.perform()
        return offset-54

    def move_to_left(self, slider, move_action_chains, offset_right):
        time.sleep(1)
        print(offset_right)
        move_action_chains.move_by_offset(-offset_right, 0).perform()


    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        cur_window_size = self.wait.until(EC.presence_of_element_located((By.ID, 'captcha-mask'))).size
        print('当前窗口大小：', cur_window_size)
        img = self.wait.until(EC.presence_of_element_located((By.ID, 'slicaptcha-img')))
        location = img.location
        size = img.size
        print('location: ', str(location))
        print('img size: ', str(size))
        # height_offset = (self.window_size['height']) // 2 - 200 - 66
        # width_offset = (self.window_size['width']) // 2 - 190 - 16
        height_offset = (self.client_height) // 2 - 200
        width_offset = (self.client_width) // 2 - 190
        # top, bottom, left, right = height_offset + location['y'], height_offset + location['y'] + size['height'], \
        #     width_offset + location['x'], width_offset + location['x'] + size['width']
        top, bottom, left, right = height_offset,  height_offset + cur_window_size['height'], width_offset, width_offset + cur_window_size['width']
        # left = self.window_size['height'] / 2 + 190
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.ID, 'slider')))
        return slider

    def get_origin_image(self, captcha_img, source_path='./image/tonghuashun'):
        """
        获取验证码原图
        :return: 图片对象
        """
        p1 = captcha_img.getpixel((0, 0))
        for img_path in os.listdir(source_path):
            src_img = Image.open(os.path.join(source_path, img_path))
            p2 = src_img.getpixel((0, 0))
            if abs(p1[0] - p2[0]) < 5:
                return src_img
        return None
            
    def get_bg_image_by_request(self, name='captcha.png'):
        img_src = self.driver.find_element(By.ID, 'slicaptcha-img').get_attribute('src')
        print(img_src)
        img = requests.get(img_src)
        img = Image.open(BytesIO(img.content))
        img.save(name)
        return img

    def get_font_image_by_request(self, name='captcha.png'):
        img_src = self.driver.find_element(By.ID, 'slicaptcha-block').get_attribute('src')
        print(img_src)
        img = requests.get(img_src)
        img = Image.open(BytesIO(img.content))
        img.save(name)
        return img

    def get_captcha_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        # top, bottom, left, right = self.get_position()
        # print('验证码位置', top, bottom, left, right)
        # screenshot = self.get_screenshot()
        # captcha = screenshot.crop((left, top, right, bottom))
        captcha = self.wait.until(EC.presence_of_element_located((By.ID, 'slicaptcha-img'))).screenshot_as_png
        captcha = Image.open(BytesIO(captcha))
        captcha.save(name)
        return captcha

    def change_to_slide(self):
        '''
        切换为滑动认证
        :return 滑动选项对象
        '''
        huadong = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,'.products-content ul > li:nth-child(2)'))
        )
        return huadong

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1: 带缺口图片
        :param image2: 不带缺口图片
        :return:
        """
        left = 60
        print(image1.size[0])
        print(image1.size[1])
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def get_gap_by_opencv(self, image_bg, image_font):
        image_bg = cv2.cvtColor(np.asarray(image_bg), cv2.COLOR_RGB2BGR)
        image_font = cv2.cvtColor(np.asarray(image_font), cv2.COLOR_RGB2BGR)
        image_bg = cv2.cvtColor(image_bg, cv2.COLOR_BGR2GRAY)
        image_font = cv2.cvtColor(image_font, cv2.COLOR_BGR2GRAY)
        # image_font = image_font[image_font.any(1)]#0表示黑色，1表示高亮部分
        result = cv2.matchTemplate(image_bg, image_font, cv2.TM_CCOEFF_NORMED)
        index_max = np.argmax(result)
        x, y = np.unravel_index(index_max, result.shape)
        print('location: ', x, y)
        return y-40

    def get_pos(self, image):
        image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        canny = cv2.Canny(blurred, 200, 400)
        contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for i, contour in enumerate(contours):
            M = cv2.moments(contour)
            if M['m00'] == 0:
                cx = cy = 0
            else:
                cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00']
            '''
            笔者是根据打印日志  来算出自己验证码的周长和大小  方法是先把所有的轮廓画出来  然后根据实际坐标 反推
            '''
            print("start")
            x, y, w, h = cv2.boundingRect(contour)
            print(x, y, w, h)
            print(cx)
            print(cv2.contourArea(contour))
            print(cv2.arcLength(contour, True))
            print("end")
            #对面积和周长进行限制
            # print("Area: ", cv2.contourArea(contour))
            # print("Length: ", cv2.arcLength(contour, True))
            if (20 < cv2.contourArea(contour) < 45 and 200 < cv2.arcLength(contour, True) < 550):
                if cx < 125:
                    continue
                x, y, w, h = cv2.boundingRect(contour) # 外接矩形
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.imshow('image', image)
                # 需要移动的距离
                print('需要移动的距离: ', x)
                return x
        return 0

    def get_pos_by_match(self, image_bg, image_font):
        # image_bg = cv2.cvtColor(np.asarray(image_bg), cv2.COLOR_RGB2BGR)
        # image_font = cv2.cvtColor(np.asarray(image_font), cv2.COLOR_RGB2BGR)
        time.sleep(1)
        image_bg = cv2.imread('captcha1.png')
        image_font = cv2.imread('captcha2.png')
        image_bg = cv2.Canny(cv2.GaussianBlur(image_bg, (3, 3), 0), 50, 150)
        image_font = cv2.Canny(cv2.GaussianBlur(image_font, (3, 3), 0), 50, 150)
        res = cv2.matchTemplate(image_font, image_bg, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc[0]  # 横坐标
        print('需要移动的距离: ', top_left)
        return top_left

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 120
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.driver).release().perform()

    def wait_pic(self):
        '''
        等待验证图片加载完成
        :return None
        '''
        # self.wait.until(
        #     # EC.presence_of_element_located((By.CSS_SELECTOR,'.geetest_popup_wrap'))
        #     EC.presence_of_element_located((By.CSS_SELECTOR,'geetest_canvas_img'))
        # )
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))
        # WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
        #     (By.XPATH, '//div[@class="ui-tab-control"]/ul/li[3]'))).click()

    def open_captcha(self):
        # self.window_size = self.driver.get_window_size()
        # print('主窗口大小：', self.window_size)
        # self.client_width=self.driver.execute_script("return document.body.offsetWidth")
        # self.client_height = self.driver.execute_script("return document.body.offsetHeight")
        # print(self.client_height, self.client_width)
        self.driver.switch_to.frame(0)
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
        print(targetOffsetX)
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

    url = 'https://www.10jqka.com.cn/index.html'
    driver.get(url)
    c = Crawler(driver)
    c.open_captcha()
    c.do_captcha()