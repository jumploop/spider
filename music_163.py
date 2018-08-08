# coding=utf-8
import requests
from lxml import etree
import re
from selenium import webdriver
from copy import deepcopy

class Music163:
    def __init__(self):
        self.start_url = "http://music.163.com/discover/playlist"
        self.headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}
    def parse_url(self,url):
        print(url)
        resp = requests.get(url,headers=self.headers)
        return resp.content.decode()

    def get_category_list(self):#获取大分类和小分类
        resp = self.parse_url(self.start_url)
        html = etree.HTML(resp)
        dl_list = html.xpath("//div[@class='bd']/dl")
        category_list = []
        for dl in dl_list:
            b_cate = dl.xpath("./dt/text()")[0] if len(dl.xpath("./dt/text()"))>0 else None
            a_list = dl.xpath("./dd/a")
            for a in a_list:
                item = {}
                item["b_cate"]= b_cate
                item["s_cate"] = a.xpath("./text()")[0] if len(a.xpath("./text()"))>0 else None
                item["s_href"] = "http://music.163.com"+a.xpath("./@href")[0] if len(a.xpath("./@href"))>0 else None
                category_list.append(item)
        return category_list

    def get_playlist_list(self,item,total_playlist_list):#获取小分类中的playlist列表
        playlist_list = []
        if item["s_href"] is not None:
            scate_resp = self.parse_url(item["s_href"])
            scate_html = etree.HTML(scate_resp)
            li_list = scate_html.xpath("//ul[@id='m-pl-container']/li")
            for li in li_list:
                item["playlist_title"] = li.xpath("./p[@class='dec']/a/@title")[0] if len(li.xpath("./p[@class='dec']/a/@title"))>0 else None
                print(item["playlist_title"])
                item["playlist_href"] = "http://music.163.com"+li.xpath("./p[@class='dec']/a/@href")[0] if len(li.xpath("./p[@class='dec']/a/@href"))>0 else None
                item["author_name"] = li.xpath("./p[last()]/a/@title")[0] if len(li.xpath("./p[last()]/a/@title"))>0 else None
                item["author_href"] = "http://music.163.com"+li.xpath("./p[last()]/a/@href")[0] if len(li.xpath("./p[last()]/a/@href"))>0 else None
                playlist_list.append(deepcopy(item))
            total_playlist_list.extend(playlist_list)
            next_url = scate_html.xpath("//a[text()='下一页']/@href")[0] if len(scate_html.xpath("//a[text()='下一页']/@href"))>0 else None
            if next_url is not None and next_url!='javascript:void(0)':
                item["s_href"] = "http://music.163.com"+next_url
                #递归，调用自己，获取下一页的播放列表，直到下一页没有的时候不再递归
                return self.get_playlist_list(item,total_playlist_list)
        return total_playlist_list

    def get_playlist_info(self,playlist): #获取单个播放别表的信息
        if playlist["playlist_href"] is not None:
            playlist_resp = self.parse_url(playlist["playlist_href"])
            playlist["covers"] = re.findall("\"images\": .*?\[\"(.*?)\"\],",playlist_resp)
            playlist["covers"] =  playlist["covers"][0] if len(playlist["covers"])>0 else None
            playlist["create_time"] = re.findall("\"pubDate\": \"(.*?)\"",playlist_resp)
            playlist["create_time"] = playlist["create_time"][0] if len(playlist["create_time"])>0 else None
            playlist_html = etree.HTML(playlist_resp)
            playlist["favorited_times"] = playlist_html.xpath("//a[@data-res-action='fav']/@data-count")[0] if len(playlist_html.xpath("//a[@data-res-action='fav']/@data-count"))>0 else None
            playlist["shared_times"] = playlist_html.xpath("//a[@data-res-action='share']/@data-count")[0] if len(playlist_html.xpath("//a[@data-res-action='share']/@data-count"))>0 else None
            playlist["desc"] = playlist_html.xpath("//p[@id='album-desc-dot']/text()")
            playlist["played_times"] = playlist_html.xpath("//strong[@id='play-count']/text()")[0] if len(playlist_html.xpath("//strong[@id='play-count']/text()"))>0 else None
            playlist["tracks"] = self.get_playlist_tracks(playlist["playlist_href"])
            return playlist

    def get_playlist_tracks(self,href): #获取每个歌单的歌曲信息
        driver = webdriver.Chrome()
        driver.get(href)
        driver.switch_to.frame("g_iframe")
        tr_list = driver.find_elements_by_xpath("//tbody/tr")
        playlist_tracks = []
        for tr in tr_list:
            track = {}
            track["name"] = tr.find_element_by_xpath("./td[2]//b").get_attribute("title")
            track["duration"] = tr.find_element_by_xpath("./td[3]/span").text
            track["singer"] = tr.find_element_by_xpath("./td[4]/div").get_attribute("title")
            track["album_name"] = tr.find_element_by_xpath("./td[5]//a").get_attribute("title")
            playlist_tracks.append(track)
        driver.quit()
        return playlist_tracks



    def run(self):
        categroy_list = self.get_category_list() #获取分类
        for cate in categroy_list:
            total_playlist_list = self.get_playlist_list(cate,[]) #获取每个分类下的所有播放列表
            print("-"*100)
            print(total_playlist_list)
            print("-"*100)
            for playlist in total_playlist_list:
                print(playlist,"*"*100)
                playlist = self.get_playlist_info(playlist)  #获取每个播放列表下的所有歌曲信息
                print(playlist)

if __name__ == '__main__':
    music_163 = Music163()
    music_163.run()
    #
    # #测试get_playlist_list
    # # test_category = {'b_cate': '语种', 's_cate': '华语', 's_href': 'http://music.163.com/discover/playlist/?cat=%E5%8D%8E%E8%AF%AD'}
    # # total_playlist_list = music_163.get_playlist_list(test_category,[])
    # # print(total_playlist_list[0])
    #
    # #测试get_playlist_info
    # test_playlist = {'b_cate': '语种', 's_cate': '华语', 's_href': 'http://music.163.com/discover/playlist/?order=hot&cat=%E5%8D%8E%E8%AF%AD&limit=35&offset=1260', 'playlist_title': '（华语）曾经的热歌，第一句歌词就是歌名', 'playlist_href': 'http://music.163.com/playlist?id=992322705', 'author_name': '你石头哥哥', 'author_href': 'http://music.163.com/user/home?id=92606854'}
    # playlist = music_163.get_playlist_info(test_playlist)
    #
    # '''
    # {'b_cate': '语种', 's_cate': '华语', 's_href': 'http://music.163.com/discover/playlist/?order=hot&cat=%E5%8D%8E%E8%AF%AD&limit=35&offset=1260', 'playlist_title': '（华语）曾经的热歌，第一句歌词就是歌名', 'playlist_href': 'http://music.163.com/playlist?id=992322705', 'author_name': '你石头哥哥', 'author_href': 'http://music.163.com/user/home?id=92606854', 'covers': 'http://p1.music.126.net/akNK49GQjbJ4pzcfbAvRlQ==/900500023154501.jpg', 'create_time': '2017-11-11T09:39:00', 'favorited_times': '2', 'shared_times': '0', 'desc': [], 'played_times': '17', 'tracks': [{'name': '火', 'duration': '03:18', 'singer': '张惠妹', 'album_name': '爱的力量\xa010年情歌最精选\xa0'}, {'name': '你 - (电视剧《孝庄秘史》主题曲)', 'duration': '04:15', 'singer': '屠洪刚', 'album_name': '自己人\xa0新歌+精选'}, {'name': '猴哥', 'duration': '02:13', 'singer': '张伟进', 'album_name': '西游记\xa0央视动画片主题曲'}, {'name': '发誓 - (电视剧《搜神传》主题曲)', 'duration': '03:16', 'singer': '钟嘉欣', 'album_name': '一人晚餐，二人世界\xa0Reloaded'}, {'name': '后来 - (原唱：刘若英)', 'duration': '05:36', 'singer': '群星', 'album_name': '爱之纪念册'}, {'name': '阿莲', 'duration': '04:26', 'singer': '戴军', 'album_name': '阿莲.新娘'}, {'name': '嘀嗒 - (电视剧《北京爱情故事》插曲)', 'duration': '04:12', 'singer': '侃侃', 'album_name': '清音流韵'}, {'name': '北极雪', 'duration': '04:13', 'singer': '陈慧琳/冯德伦', 'album_name': '音乐记事本'}, {'name': '好运来', 'duration': '03:33', 'singer': '祖海', 'album_name': '再唱为了谁'}, {'name': '嘻唰唰', 'duration': '03:37', 'singer': '花儿乐队', 'album_name': '花季王朝'}, {'name': '好春光 - (电视剧《春光灿烂猪八戒》主题曲)', 'duration': '03:37', 'singer': '吴彤', 'album_name': '好春光'}, {'name': '错错错', 'duration': '04:47', 'singer': '六哲/陈娟儿', 'album_name': '网络新四大天王'}, {'name': '董小姐', 'duration': '05:13', 'singer': '宋冬野', 'album_name': '安和桥北'}, {'name': '无所谓', 'duration': '04:24', 'singer': '杨坤', 'album_name': '无所谓'}, {'name': '下雨天', 'duration': '04:13', 'singer': '南拳妈妈', 'album_name': '心情出口'}, {'name': '当你老了 - (电视剧《嘿！老头》片尾曲)', 'duration': '05:10', 'singer': '赵照', 'album_name': '当你老了'}, {'name': '痛快(Live)', 'duration': '03:16', 'singer': 'S.H.E', 'album_name': '江苏卫视\xa02016\xa0跨年演唱会'}, {'name': '蚂蚁\xa0蚂蚁', 'duration': '05:20', 'singer': '张楚', 'album_name': '摇滚中国乐势力'}, {'name': '有一个姑娘 - (中视《还珠格格2》片尾曲)', 'duration': '03:33', 'singer': '赵薇', 'album_name': '还珠格格\xa0音乐全记录'}, {'name': '春天花会开', 'duration': '04:01', 'singer': '林志伟', 'album_name': '林志伟作品集'}, {'name': '跟着感觉走', 'duration': '04:02', 'singer': '苏芮', 'album_name': '回首'}, {'name': '分开不一定分手', 'duration': '03:23', 'singer': '山野', 'album_name': '说。'}, {'name': '想把我唱给你听', 'duration': '04:49', 'singer': '老狼/王婧', 'album_name': '热门华语202'}, {'name': '今天是你的生日', 'duration': '05:02', 'singer': '董文华', 'album_name': '金曲20年'}, {'name': '玫瑰玫瑰我爱你', 'duration': '02:26', 'singer': '王若琳', 'album_name': 'The\xa0Adult\xa0Storybook'}, {'name': '爱我就跟我走', 'duration': '04:13', 'singer': '王鹤铮', 'album_name': '爱我就跟我走'}, {'name': '为了爱\xa0梦一生', 'duration': '04:39', 'singer': '王杰', 'album_name': '为了爱\xa0梦一生'}, {'name': '猜不透\xa0cover.丁当', 'duration': '03:53', 'singer': '菌菌酱', 'album_name': '猜不透\xa0cover.丁当'}, {'name': '我爱你，塞北的雪', 'duration': '02:56', 'singer': '殷秀梅', 'album_name': '名歌经典'}, {'name': '我们好像在哪见过 - (电视剧《咱们结婚吧》片尾曲)', 'duration': '03:16', 'singer': '杨宗纬/叶蓓', 'album_name': '咱们结婚吧\xa0电视原声带'}, {'name': '花儿为什么这样红', 'duration': '04:20', 'singer': '艾尔肯', 'album_name': '走出沙漠的刀郎'}, {'name': '妹妹你大胆地往前走 - (故事片《红高梁》插曲)', 'duration': '02:08', 'singer': '姜文', 'album_name': '记忆的符号-中国电影百年寻音集\xa0CD26'}, {'name': '在那桃花盛开的地方', 'duration': '03:31', 'singer': '蒋大为', 'album_name': '牡丹之歌'}, {'name': '看月亮爬上来（Cover\xa0张杰）', 'duration': '03:17', 'singer': '戴立', 'album_name': '摘星星（戴立翻唱合辑）'}, {'name': '天不下雨天不刮风天上有太阳', 'duration': '05:06', 'singer': '尹相杰/于文华', 'album_name': '20世纪中华歌坛名人百集珍藏版'}, {'name': '任贤齐\xa0-\xa0对面的女孩看过来\xa0(Crazy\xa0Up!\xa02015\xa0Mix)', 'duration': '04:09', 'singer': 'Crazy Up!', 'album_name': '对面的女孩看过来'}, {'name': 'I\xa0Love\xa0You(爱很简单)', 'duration': '05:16', 'singer': '王若琳', 'album_name': 'Start\xa0From\xa0Here'}, {'name': '你是风儿我是沙', 'duration': '04:42', 'singer': '林心如/周杰', 'album_name': '还珠格格\xa0音乐全记录'}, {'name': '我的心好冷', 'duration': '05:21', 'singer': 'Sara', 'album_name': '我的心好冷'}, {'name': '真的好想你 - (电视剧《梦圆何方》主题曲)', 'duration': '04:18', 'singer': '周冰倩', 'album_name': '真的好想你(珍藏精选)'}, {'name': 'I\xa0Believe - (《我的野蛮女友》主题曲)', 'duration': '04:49', 'singer': '范逸臣', 'album_name': 'Forever\xa0Love\xa034首动人国语精选情歌'}, {'name': '天上人间', 'duration': '04:09', 'singer': '古巨基', 'album_name': '还珠格格3天上人间\xa0音乐全纪录'}, {'name': '给我一个吻 - (电影《重返20岁》插曲)', 'duration': '02:56', 'singer': '杨子姗', 'album_name': '重返20岁\xa0电影原声带'}, {'name': '没有情人的情人节', 'duration': '04:13', 'singer': '孟庭苇', 'album_name': '冬季到台北来看雨'}, {'name': '我的心里只有你没有他', 'duration': '03:20', 'singer': 'M-PHOTOS', 'album_name': '我的心里只有你'}, {'name': '等你爱我 - (电影《将爱情进行到底》片尾曲)', 'duration': '04:40', 'singer': '陈奕迅', 'album_name': 'Stranger\xa0Under\xa0My\xa0Skin'}, {'name': '死了都要爱', 'duration': '04:29', 'singer': '信乐团', 'album_name': '挑信'}, {'name': '没那么简单', 'duration': '05:08', 'singer': '黄小琥', 'album_name': '简单/不简单'}, {'name': '世上只有妈妈好', 'duration': '02:23', 'singer': '群星', 'album_name': '中国最爱儿歌经典一'}, {'name': '明明白白我的心(Live)', 'duration': '02:22', 'singer': '周杰伦/成龙', 'album_name': '\xa0热门华语281'}, {'name': '走在乡间的小路上', 'duration': '03:11', 'singer': '杨烁', 'album_name': '杨烁同名专辑'}, {'name': '栀子花开', 'duration': '03:55', 'singer': '何炅', 'album_name': '可以爱'}, {'name': '客官不可以', 'duration': '03:47', 'singer': '徐良/小凌', 'album_name': '犯贱'}, {'name': '考试什么的都去死吧', 'duration': '03:38', 'singer': '徐良/庄雨洁', 'album_name': '不良少年'}, {'name': '冬季到台北来看雨', 'duration': '05:05', 'singer': '孟庭苇', 'album_name': '国语真经典:\xa0孟庭苇'}, {'name': '好想好想 - (电视剧《情深深雨濛濛》片尾曲)', 'duration': '03:36', 'singer': '古巨基', 'album_name': '情深深雨蒙蒙音乐全记录1'}, {'name': '难忘今宵', 'duration': '02:14', 'singer': '群星', 'album_name': '2014年央视春晚'}, {'name': '三月里的小雨', 'duration': '03:51', 'singer': '刘文正', 'album_name': '三月里的小雨'}, {'name': '沧海一声笑 - (电影《笑傲江湖》主题曲)', 'duration': '02:57', 'singer': '许冠杰', 'album_name': '沧海一声笑'}, {'name': '白月光 - (电视剧《出水芙蓉》片头曲)', 'duration': '04:27', 'singer': '张信哲', 'album_name': '下一个永远'}, {'name': '千年等一回 - (电视剧《新白娘子传奇》主题曲)', 'duration': '03:35', 'singer': '高胜美', 'album_name': '新白娘子传奇\xa0电视原声带'}, {'name': '忽然之间 - (原唱：莫文蔚《忽然之间》)', 'duration': '03:22', 'singer': '巴士那', 'album_name': '热门华语267'}, {'name': '我会好好的', 'duration': '04:30', 'singer': '王心凌', 'album_name': 'Cyndi\xa0With\xa0U'}, {'name': '再回首', 'duration': '04:16', 'singer': '姜育恒', 'album_name': '不朽金曲精选\xa0Ⅰ'}, {'name': '为你我受冷风吹', 'duration': '04:21', 'singer': '林忆莲', 'album_name': 'Sandy\xa0Lam\xa0Concert\xa0MMXI\xa0演唱会'}, {'name': 'Hey\xa0Jude', 'duration': '04:37', 'singer': '孙燕姿', 'album_name': 'Start\xa0自选集'}, {'name': '阴天', 'duration': '04:02', 'singer': '莫文蔚', 'album_name': '就\xa0i\xa0Karen\xa0莫文蔚精选'}, {'name': '他不爱我', 'duration': '03:58', 'singer': '莫文蔚', 'album_name': '就\xa0i\xa0Karen\xa0莫文蔚精选'}, {'name': '爱是你我', 'duration': '04:29', 'singer': '刀郎', 'album_name': '我们的爱我不放手'}, {'name': '2002年的第一场雪', 'duration': '04:15', 'singer': '刀郎', 'album_name': '谢谢你'}, {'name': '就在', 'duration': '03:36', 'singer': '张悬', 'album_name': '城市'}, {'name': '如果你要离去', 'duration': '03:37', 'singer': '张悬', 'album_name': '如果你冷'}, {'name': '怎么可', 'duration': '04:11', 'singer': '张敬轩', 'album_name': '是时候…'}, {'name': '口是心非', 'duration': '04:52', 'singer': '张雨生', 'album_name': '口是心非'}, {'name': '我期待', 'duration': '05:51', 'singer': '张雨生', 'album_name': '如燕盘旋而来的思念'}, {'name': '山不转水转 - (电视剧《山不转水转》主题曲)', 'duration': '03:11', 'singer': '那英', 'album_name': '20世纪中华歌坛名人百集珍藏版'}, {'name': '雾里看花', 'duration': '04:06', 'singer': '那英', 'album_name': '20世纪中华歌坛名人百集珍藏版'}, {'name': '浏阳河(Live)', 'duration': '03:29', 'singer': '宋祖英', 'album_name': '中国北京鸟巢夏季音乐会'}, {'name': '辣妹子', 'duration': '03:19', 'singer': '宋祖英', 'album_name': '20世纪中华歌坛名人百集珍藏版'}, {'name': '甜蜜蜜 - (Sweet)', 'duration': '03:31', 'singer': '邓丽君', 'album_name': '邓丽君15周年·30周年(限量版)'}, {'name': '又见炊烟', 'duration': '02:53', 'singer': '邓丽君', 'album_name': '又见炊烟'}, {'name': '等你一万年', 'duration': '04:00', 'singer': '杨钰莹', 'album_name': '轻轻的告诉你'}, {'name': '我不想说 - (电视剧《外来妹》主题曲)', 'duration': '04:29', 'singer': '杨钰莹', 'album_name': '轻轻的告诉你'}]}
    # '''
