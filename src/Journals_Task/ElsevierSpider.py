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
from src.journal_parser.Elsevier_Parser import *
from src.crawl_tools.request_with_proxy import request_with_random_ua

class ElsevierSpider:
    '''
        sample_url: http://www.sciencedirect.com/science/journal/15708268
    '''
    def __init__(self,start_url):
        self.url = start_url

    def run(self):
        #自动切换不同年代不同卷volume的页面，得到所有结果
        for volume_area_link in ElsevierAllItemsPageParser(
            html_source = request_with_random_ua(self.url).text
        ).volume_area_links:
            print(volume_area_link)
            volume_links = ElsevierAllItemsPageParser(
                html_source = request_with_random_ua(volume_area_link).text
            ).volume_links
            volume_links.append(volume_area_link)
            for volume_link in volume_links:
                print(volume_link)
                for sec in ElsevierAllItemsPageParser(
                    html_source = request_with_random_ua(volume_link).text
                ).secs:
                    article = ElsevierAricle(sec)
                    if article.type=='Original Research Article':
                        print(article.title)
                        #article.save_to_db()
                    print('----------')
            print('===================')
        print('ok')

if __name__=="__main__":
    ElsevierSpider(
        start_url = 'http://www.sciencedirect.com/science/journal/15708268',
    ).run()