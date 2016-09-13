#coding:utf-8
"""
@file:      Elsevier_pdf_url_generator.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-06 13:18
@description:
            从db中获得elsevier杂志社的文章title集合，
            生成pdf_url反馈给db
"""
import sys,os
up_level_N = 2
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from journal_parser.Elsevier_Parser import Elsevier_Parser
from PdfUrlGenerator import *

def get_elsevier_pdf_url_func(driver,unfinished_item):
    #print('url:{}'.format(unfinished_item[0]))
    return Elsevier_Parser(
        article_page_url = unfinished_item[0],
        driver = driver
    ).pdf_url


class Elsevier_pdf_url_generator(PdfUrlGenerator):
    def __init__(self):
        PdfUrlGenerator.__init__(self)

    def get_unfinished_items(self,length):
        return self._get_unfinished_items(
            query_sql = self.query_sql,
            max_id_where_sqls=[
                ['resource_link','is','null'],
                ['journal_temp_info','like','%Elsevier%']
            ],
            length = length
        )

    def generate(self,unfinished_item):
        return self._generate(unfinished_item,
            google_id_index = 1,
            get_pdf_url_func = get_elsevier_pdf_url_func
        )

    def run(self,thread_counts=16,visual=True,limit=1000,length=1000):
        self.query_limit = limit
        self._run(thread_counts,visual)
        self.query_sql = "select link,google_id from articles where resource_link is null \
                  and journal_temp_info like '%Elsevier%' limit {}".format(limit)
        self._task_thread_pool.map(self.generate,self.get_unfinished_items(length))
        self._close()


if __name__=='__main__':
    from crawl_tools.WatchDog import close_procs_by_keyword

    visual = False

    if visual:
        close_procs_by_keyword(keyword='chrome')
    else:
        close_procs_by_keyword(keyword='phantom')

    Elsevier_pdf_url_generator().run(
        thread_counts=8,
        visual=visual,
        limit=1000000,
        length=100000
    )
