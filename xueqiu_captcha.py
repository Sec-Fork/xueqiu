

import time
import random
from io import BytesIO
from PIL import Image
import logger
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
        self.logger = logger.Logger(filename=logname, level='DEBUG').loggerImp()

    def do_captcha(self):
        du = DragUtil(self.driver, self.logger)

        try:
            # 确认图片加载完成
            self.wait_pic()
            time.sleep(2)
            # 获取滑块
            slider = self.get_slider()
            # 获取带缺口验证码图片
            image1 = self.get_geetest_image('captcha1.png')
            # 获取不带缺口的验证码图片
            self.delete_style()
            image2 = self.get_geetest_image('captcha2.png')
            #self.delete_style_test()
            # 获取缺口位置
            gap = self.get_gap(image2, image1)
            # 减去缺口位移
            gap -= BORDER
            du.simulateDragX(slider, gap)
            success = self.wait.until(
                EC.visibility_of(self.driver.find_element(By.CLASS_NAME, 'geetest_panel_success'))
            )
            self.logger.info('验证成功')
            time.sleep(1)
        except Exception as e:
            self.logger.error('失败，再来一次')
            self.logger.error(e)
            time.sleep(1)
            self.refresh()
            time.sleep(1)
            self.do_captcha()

    def refresh(self,):
        self.logger.info('刷新验证码')
        r = self.driver.find_element(By.CLASS_NAME, 'geetest_panel_error_content')
        ActionChains(self.driver).move_to_element(r).click(r).perform()
        self.logger.info('验证码刷新成功')

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
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
        # slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        time.sleep(2)
        slider = self.driver.find_element(By.CLASS_NAME, "geetest_slider_button")
        return slider

    def get_geetest_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        self.logger.info(('获得验证码位置: ', top, bottom, left, right))
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def delete_style(self):
        '''
        执行js脚本，获取无滑块图
        :return None
        '''
        js = 'document.querySelectorAll("canvas")[2].style=""'
        self.driver.execute_script(js)

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
        self.logger.info('获得偏移量: {}'.format(left))
        return left

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
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def wait_pic(self):
        '''
        等待验证图片加载完成
        :return None
        '''
        self.logger.info('等待加载图片')
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))
        


class DragUtil():
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger

    def __getRadomPauseScondes(self):
        """
        :return:随机的拖动暂停时间
        """
        return random.uniform(0.6, 0.9)

    def simulateDragX(self, source, targetOffsetX):
        """
        模仿人的拖拽动作：快速沿着X轴拖动（存在误差），再暂停，然后修正误差
        防止被检测为机器人，出现“图片被怪物吃掉了”等验证失败的情况
        :param source:要拖拽的html元素
        :param targetOffsetX: 拖拽目标x轴距离
        :return: None
        """
        self.logger.info('开始拖动滑块')
        action_chains = webdriver.ActionChains(self.driver)
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
            self.logger.error('滑块拖动出现问题')
            raise Exception("莫不是系统出现了问题？!")

        # 参考action_chains.drag_and_drop_by_offset()
        action_chains.release()
        action_chains.perform()
        self.logger.info('滑块拖动完成')


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