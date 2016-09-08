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
from journal_parser.Elsevier_Parser import Elsevier_Parser
from journal_pdf_url_generators.PdfUrlGenerator import *

def get_elsevier_pdf_url_func(driver,unfinished_item):
    #print('url:{}'.format(unfinished_item[0]))
    return Elsevier_Parser(
        article_page_url = unfinished_item[0],
        driver = driver
    ).pdf_url


class Elsevier_pdf_url_generator(PdfUrlGenerator):
    def __init__(self):
        PdfUrlGenerator.__init__(self)

    def get_unfinished_items(self):
        ret = self._get_unfinished_items(self.query_sql)
        print('Elsevier_pdf_url_generator:\n\tGot {} new items in limit {}...'.format(len(ret),self.query_limit))
        return ret

    def generate(self,unfinished_item):
        return self._generate(unfinished_item,
            google_id_index = 1,
            get_pdf_url_func = get_elsevier_pdf_url_func
        )

    def run(self,thread_counts=16,visual=True,limit=1000):
        self.query_limit = limit
        self._run(thread_counts,visual)
        self.query_sql = "select link,google_id from articles where resource_link is null \
                  and journal_temp_info like '%Elsevier%' limit {}".format(limit)
        self._task_thread_pool.map(self.generate,self.get_unfinished_items())
        self._close()


if __name__=='__main__':
    from crawl_tools.WatchDog import close_procs_by_keyword

    visual = False

    if visual:
        close_procs_by_keyword(keyword='chrome')
    else:
        close_procs_by_keyword(keyword='phantom')

    Elsevier_pdf_url_generator().run(thread_counts=8,visual=visual,limit=1000)
