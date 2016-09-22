#coding:utf-8
"""
@file:      ElsevierSpider.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-17 19:56
@description:
            Elsevier针对某特定journal获取其古往今来的所有文章的爬虫
            上级模块有多线程分配，故此处用单线程写
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from bs4 import BeautifulSoup
from Journals_Task.JournalSpider import JournalSpider
from crawl_tools.request_with_proxy import request_with_random_ua
from journal_parser.Elsevier_Parser import ElsevierAricle,ElsevierAllItemsPageParser
import time,psycopg2


class ElsevierSpider(JournalSpider):
    '''
        sample_url: http://www.sciencedirect.com/science/journal/15708268
    '''
    def __init__(self,JournalObj,driverObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.driverObj = driverObj
        self.JournalObj = JournalObj
        self.handle_sciencedirect_url()
        self.get_unfinished_volume_links()

    def handle_sciencedirect_url(self):
        #print(self.url)
        if 'sciencedirect' in self.url:
            return
        try:
            resp = request_with_random_ua(self.url)
            html = resp.text
            #print('by request ok')
            method = 'request'
        except Exception as e:
            print('Handle URL:  request error:{}'.format(str(e)))
            driver = self.driverObj.engine
            while(1):
                try:
                    driver.get(self.url)
                    time.sleep(2)
                    html = driver.page_source
                    break
                except Exception as e:
                    print('[Error] in ElsevierSpider:init_url:\n{}'.format(str(e)))
                    time.sleep(2)
            method = 'driver'
        self.driverObj.status = 'free'
        soup = BeautifulSoup(html,'lxml')
        if method == 'request':
            jouranl_index = soup.select_one('.cta-primary')['href'].split('/')[0].split('-')
            self.url = 'http://www.sciencedirect.com/science/journal/{}'\
                .format(jouranl_index[0]+jouranl_index[1])
        else:
            self.url = soup.select_one('.view-articles')['href']

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            return
        #假如数据库中已保存，直接读取即可，无需生成
        for volume_area_link in ElsevierAllItemsPageParser(
            html_source = request_with_random_ua(self.url).text
        ).volume_area_links:
            #先分volume年份区间（十年）
            print(volume_area_link)
            area_volume_links = ElsevierAllItemsPageParser(
                html_source = request_with_random_ua(volume_area_link).text
            ).volume_links
            area_volume_links.append(volume_area_link)
            #得到该区间所有年份的page_url
            self.volume_links.extend(area_volume_links)

    def run(self):
        unfinished_links = self.get_unfinished_volume_links()
        for volume_link in unfinished_links:
            print(volume_link)
            parser = ElsevierAllItemsPageParser(
                html_source = request_with_random_ua(volume_link).text
            )
            for sec in parser.secs:
                try:
                    article = ElsevierAricle(sec,JournalObj,parser.volume_year)
                except Exception as e:
                    continue
                if article.type:
                    while(1):
                        try:
                            article.save_to_db()
                            break
                        except psycopg2.OperationalError:
                            print('db error,again')
                            time.sleep(2)
            if len(parser.secs)>0:
                self.mark_volume_ok(volume_link)
        if len(unfinished_links)>0:
            self.mark_journal_ok()


if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    from crawl_tools.DriversPool import Driver
    JournalObj=Journal()
    JournalObj.site_source = 'http://www.elsevier.com/wps/find/journaldescription.cws_home/505606/description#description'
    JournalObj.sjr_id = 123
    ElsevierSpider(
        JournalObj=JournalObj,
        driverObj=Driver(visual=True)
    ).run()