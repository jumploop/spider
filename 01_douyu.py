import json
import time
from selenium import webdriver


class DouYu(object):
    def __init__(self):
        self.start_url = 'https://www.douyu.com/directory/all'
        self.driver = webdriver.Chrome()
        self.index=1

    def get_content_list(self):  # 提取数据
        li_list = self.driver.find_elements_by_xpath('//ul[@id="live-list-contentbox"]/li')
        content_list = []
        for li in li_list:
            item = {}
            item['title'] = li.find_element_by_xpath('./a').get_attribute('title')
            item['anchor'] = li.find_element_by_xpath('.//span[@class="dy-name ellipsis fl"]').text
            item['watch_num'] = li.find_element_by_xpath('.//span[@class="dy-num fr"]').text
            item['image'] = li.find_element_by_xpath('.//img[@class="JS_listthumb"]').get_attribute('src')
            item['category'] = li.find_element_by_xpath('.//span[@class="tag ellipsis"]').text
            print(item)
            content_list.append(item)
        # 提取下一页元素
        next_url = self.driver.find_elements_by_xpath('.//a[@class="shark-pager-next"]')
        next_url = next_url[0] if len(next_url) > 0 else None
        return content_list, next_url

    def save_content_list(self, content_list):
        json_str = json.dumps(content_list, ensure_ascii=False, indent=4)
        with open('./douyu/douyu_{}'.format(str(self.index)) + '页.json', 'w', encoding='utf-8') as f:
            f.write(json_str)
        self.index += 1

    def run(self):  # 实现主要逻辑
        # start_url
        # 发送请求,获取响应
        self.driver.get(self.start_url)

        # 提取数据
        content_list, next_url = self.get_content_list()
        # 保存
        self.save_content_list(content_list)
        # 下一页数据的提取
        while next_url is not None:
            next_url.click()# 页面没有完全加载完
            time.sleep(5)
            content_list, next_url = self.get_content_list()
            # 保存
            self.save_content_list(content_list)

if __name__ == '__main__':
    douyu=DouYu()
    douyu.run()