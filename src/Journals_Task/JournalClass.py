#coding:utf-8
"""
@file:      JournalClass.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-19 21:40
@description:
            杂志社 ORM 对象
"""

class Journal:
    def __init__(self):
        self.sjr_id = None
        self.name = None
        self.country = None
        self.site_source = None
        self.area_relation_cot = None
        self.category_relation_cot = None
        self.issn = None
        self.is_crawled_all_article = None
        self.open_access = None
        self.h_index = None
        self.publisher = None