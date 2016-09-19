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


class ElsevierSpider(JournalSpider):
    '''
        sample_url: http://www.sciencedirect.com/science/journal/15708268
    '''
    def __init__(self,url,journal_id):
        JournalSpider.__init__(journal_id)
        self.url = url
        self.handle_sciencedirect_url()

    def handle_sciencedirect_url(self):
        if 'sciencedirect' not in self.url:
            resp = request_with_random_ua(self.url)
            self.url = BeautifulSoup(resp.text,'lxml')\
                .select('.cta-generic')[-1].select_one('a')['href']
        print(self.url)

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
                    article = ElsevierAricle(sec)
                    if article.type:
                        print(article.title)
                        #article.save_to_db()
                    print('----------')
            print('===================')
        #self.mark_journal_ok()


if __name__=="__main__":
    ElsevierSpider(
        #url = 'http://www.sciencedirect.com/science/journal/15708268',
        url = 'http://www.journals.elsevier.com/journal-of-network-and-computer-applications/',
        journal_id = 123
    ).run()