#coding:utf-8
"""
@file:      SpringSpider.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-17 19:56
@description:
            ??
"""

from src.db_config import new_db_cursor
from src.journal_parser.Spring_Parser import *


class SpringSpider:
    '''
        sample_url: http://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=778
    '''
    def __init__(self):
        self.cur = new_db_cursor()