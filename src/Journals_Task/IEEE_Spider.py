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
from src.journal_parser.IEEE_Parser import IEEE_HTML_Parser

class IEEE_Spider(JournalSpider):
    '''
       sample_url: http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=5480&punumber=83
    '''
    def __init__(self,url,journal_id):
        JournalSpider.__init__(self,journal_id)
        self.url = url