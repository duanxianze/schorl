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
from bs4 import BeautifulSoup
from src.Journals_Task.JournalSpider import JournalSpider
from src.crawl_tools.request_with_proxy import request_with_random_ua
from src.journal_parser.Elsevier_Parser import ElsevierAricle,ElsevierAllItemsPageParser
import time


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
        print(self.driverObj)

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

    def run(self):
        #自动切换不同年代不同卷volume的页面，得到所有结果
        for volume_area_link in ElsevierAllItemsPageParser(
            html_source = request_with_random_ua(self.url).text
        ).volume_area_links:
            #先分volume年份区间（十年）
            print(volume_area_link)
            volume_links = ElsevierAllItemsPageParser(
                html_source = request_with_random_ua(volume_area_link).text
            ).volume_links
            volume_links.append(volume_area_link)
            #得到该区间所有年份的page_url
            for volume_link in volume_links:
                print(volume_link)
                for sec in ElsevierAllItemsPageParser(
                    html_source = request_with_random_ua(volume_link).text
                ).secs:
                    article = ElsevierAricle(sec,self.JournalObj)
                    if article.type:
                        article.show_in_cmd()
                        #print(article.title)
                        #article.save_to_db()
                    print('----------')
            print('===================')
        #self.mark_journal_ok()


if __name__=="__main__":
    from src.Journals_Task.JournalClass import Journal
    from src.crawl_tools.DriversPool import Driver
    JournalObj=Journal()
    JournalObj.site_source = 'http://www.elsevier.com/wps/find/journaldescription.cws_home/505606/description#description'
    JournalObj.sjr_id = 123
    ElsevierSpider(
        JournalObj=JournalObj,driverObj=Driver(visual=True)
    ).run()