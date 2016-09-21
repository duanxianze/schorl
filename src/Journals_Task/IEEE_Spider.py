#coding:utf-8
"""
@file:      IEEE_Spider.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-17 19:55
@description:
            ??
"""
from src.Journals_Task.JournalSpider import JournalSpider
from src.journal_parser.IEEE_Parser import *
from src.crawl_tools.request_with_proxy import request_with_random_ua


class IEEE_Spider(JournalSpider):
    '''
       sample_url: http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=5480&punumber=83
    '''
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source

    def run(self):
        html = request_with_random_ua(self.url).text
        print(html)


if __name__=="__main__":
    from src.Journals_Task.JournalClass import Journal
    from src.crawl_tools.DriversPool import Driver
    JournalObj=Journal()
    JournalObj.site_source = 'http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=5480&punumber=83'
    JournalObj.sjr_id = 123
    IEEE_Spider(JournalObj).run()