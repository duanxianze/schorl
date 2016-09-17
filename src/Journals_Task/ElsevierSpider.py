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

class ElsevierSpider:
    '''
        sample_url: http://www.sciencedirect.com/science/journal/15708268
    '''
    def __init__(self):
        self.cur = new_db_cursor()
