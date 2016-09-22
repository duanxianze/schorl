#coding:utf-8
"""
@file:      JournalSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-19 9:15
@description:
            The basic class of journal spider which contains public methods.
"""
from src.db_config import new_db_cursor

class JournalSpider:
    def __init__(self,JournalObj):
        self.JournalObj = JournalObj

    def mark_journal_ok(self):
        cur = new_db_cursor()
        cur.execute(
            'upadte journal set is_crawled_all_article = true\
             where journal_id = {}'.format(self.JournalObj.sjr_id)
        )
        cur.close()

    def handle_db_url(self):
        pass