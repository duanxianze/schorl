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
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from db_config import new_db_cursor

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