# 滑动验证码

## 雪球自动滑动验证码

1. 导入文件 `from xueqiu_captcha import Crawler as XC`
2. driver 初始化传入参数
   ```python
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
   ```
3. 初始化，传入 driver `xc = XC(driver)`
4. 在出现验证码的地方执行自动划验证码方法即可。`xc.do_captcha()`, 若划动不成功，方法会等待2s自动刷新验证码重新自动划动。
5. 注意：系统缩放和浏览器缩放都需要是 100%。验证码需要显示出来才能执行成功。


## 同花顺自动滑动验证码

1. 导入文件 `from ths_captcha import Crawler as TC`
2. driver 初始化传入参数
   ```python
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
   ```
3. 初始化，传入 driver `xc = XC(driver)`。若验证码在网页的iframe中，需要先将driver转入frame：`driver.switch_to.frame(0)`再传入`xc = XC(driver)`。具体查看文件`main`函数。
4. 在出现验证码的地方执行自动划验证码方法即可。`xc.do_captcha()`, 若不成功，方法会重新自动划动。
5. 注意：系统缩放和浏览器缩放都需要是 100%。验证码需要显示出来才能执行成功。