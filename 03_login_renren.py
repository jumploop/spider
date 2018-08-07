import time

from selenium import webdriver

driver=webdriver.Chrome()
driver.get('http://www.renren.com/')
driver.find_element_by_id('email').send_keys('13146128763')
driver.find_element_by_id('password').send_keys('zhoudawei123')
time.sleep(3)
driver.find_element_by_id('login').click()
time.sleep(3)
driver.quit()