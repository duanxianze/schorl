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
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)


from db_config import DB_CONNS_POOL

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
        self.volume_links_got = None
        self.area_id = None
        self.category_id = None

    def generate_area_category_id(self):
        if self.area_relation_cot:
            self.area_id = self.get_area_ids()[0][0]
        if self.category_relation_cot:
            self.category_id = self.get_category_ids()[0][0]

    def get_category_ids(self):
        cur = DB_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select category_id from journal_category \
            where journal_id={}'.format(self.sjr_id)
        )
        data = cur.fetchall()
        cur.close()
        return data

    def get_area_ids(self):
        cur = DB_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select area_id from journal_area \
            where journal_id={}'.format(self.sjr_id)
        )
        data = cur.fetchall()
        cur.close()
        return data
