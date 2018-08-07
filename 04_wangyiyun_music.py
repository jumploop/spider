import json
import time

import requests
from selenium import webdriver
from lxml import etree


class Music_163(object):
    def __init__(self):
        self.start_url = 'https://music.163.com/discover/playlist'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
        }
        self.part_url = 'https://music.163.com'
        self.driver = webdriver.Chrome()
        # self.proxies = {'https': 'https://139.224.80.139:3128'}
        self.index = 1

    def parse_url(self, url):  # 发送请求,获取响应
        response = requests.get(url, headers=self.headers)
        return response.content

    def get_category_list(self, html_str):  # 获取分类内容
        """获取分类列表"""
        html = etree.HTML(html_str)
        dl_list = html.xpath('//div[@class="bd"]/dl')
        category_list = []
        for dl in dl_list:
            b_item = {}
            b_item['b_cate'] = dl.xpath('./dt/text()')[0]  # 大分类
            b_item['b_list'] = []  # 具体分类列表
            a_list = dl.xpath('./dd/a')
            for a in a_list:
                s_item = {}
                s_item['s_cate'] = a.xpath('./text()')[0]  # 小分类
                s_item['s_href'] = self.part_url + a.xpath('./@href')[0]  # 链接地址
                s_item['play_list'] = self.get_play_list(s_item['s_href'], [])
                b_item['b_list'].append(s_item)
                print(s_item)
            category_list.append(b_item)

        return category_list

    def get_play_list(self, url, play_list):
        """
        获取小分类的播放列表
        :param url:
        :return:
        """
        self.driver.get(url)
        time.sleep(3)
        self.driver.switch_to.frame('g_iframe')
        li_list = self.driver.find_elements_by_xpath('//ul[@id="m-pl-container"]/li')
        for li in li_list:
            item = {}
            item['title'] = li.find_element_by_xpath('./p[@class="dec"]/a').get_attribute('title')
            item['href'] = li.find_element_by_xpath('./p[@class="dec"]/a').get_attribute('href')
            item['author_name'] = li.find_element_by_xpath('./p[last()]/a').get_attribute('title')
            item['author_href'] = li.find_element_by_xpath('./p[last()]/a').get_attribute('href')
            item['img'] = li.find_element_by_xpath('./div/img').get_attribute('src')
            print(item)
            play_list.append(item)
        # 获取下一页链接
        next_url = self.driver.find_element_by_xpath('//a[text()="下一页"]').get_attribute('href')
        if next_url is not None and next_url != 'javascript:void(0)':
            return self.get_play_list(next_url, play_list)
        else:
            return play_list

    def save_content_list(self, content_list):
        json_str = json.dumps(content_list, ensure_ascii=False, indent=4)

        with open('./163/163_{}'.format(str(self.index)) + '页.json', 'w', encoding='utf-8') as f:
            f.write(json_str)
        self.index += 1

    def run(self):  # 实现主逻辑
        # start_url
        # 发送请求,获取响应
        html_str = self.parse_url(self.start_url)
        # 提取分类列表
        category_list = self.get_category_list(html_str)
        # 保存
        self.save_content_list(category_list)


if __name__ == '__main__':
    music = Music_163()
    music.run()
