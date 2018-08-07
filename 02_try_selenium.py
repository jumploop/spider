import time

from selenium import webdriver

driver = webdriver.Chrome()
# 调整浏览器窗口的大小
driver.maximize_window()  # 最大化
# driver.set_window_size(1366,768)

driver.get('https://www.baidu.com')
# 屏幕截图
# driver.save_screenshot('百度.png')
# 在input标签输入内容
driver.find_element_by_id('kw').send_keys('长城')  # 输入内容
driver.find_element_by_id('su').click()  # 点击元素
# 获取网页源码
# print(driver.page_source)
# 获取当前URL
# print(driver.current_url)
cookie=driver.get_cookies()
print(cookie)
time.sleep(5)
driver.quit()  # 退出浏览器
