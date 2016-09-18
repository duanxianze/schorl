#coding:utf-8
"""
@file:      ElsevierSpider.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-17 19:56
@description:
            ??
"""
from src.db_config import new_db_cursor
from src.journal_parser.Elsevier_Parser import *
from src.crawl_tools.request_with_proxy import request_with_random_ua
from src.crawl_tools.DriversPool import DriversPool
import time,requests

class ElsevierSpider:
    '''
        sample_url: http://www.sciencedirect.com/science/journal/15708268
    '''
    def __init__(self,url):
        self.cur = new_db_cursor()
        self.url = url

    def run(self):
        '''
        pool = DriversPool(1)
        driverObj = pool.get_one_free_driver()
        driver = driverObj.engine
        driver.get(self.url)
        driverObj.status = 'free'
        time.sleep(2)
        ElsevierAllItemsPageParser(html_source=driver.page_source)
        time.sleep(10)
        '''
        resp = request_with_random_ua(self.url)
        parser = ElsevierAllItemsPageParser(
            html_source = resp.text
        )
        for volume in parser.volumes:
            print(volume)

        print('ok')
        time.sleep(555)

        for sec in parser.secs:
            article = ElsevierAricle(sec)
            if article.type=='Original Research Article':
                article.show_in_cmd()
            print('----------')

if __name__=="__main__":
    ElsevierSpider(
        url = 'http://www.sciencedirect.com/science/journal/15708268',
    ).run()