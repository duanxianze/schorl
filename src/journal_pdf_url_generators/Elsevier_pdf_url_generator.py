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
from src.journal_parser.Elsevier_Parser import Elsevier_Parser
from PdfUrlGenerator import *

def get_elsevier_pdf_url_func(driver,unfinished_item):
    return Elsevier_Parser(
        article_page_url = unfinished_item[0],
        driver = driver
    ).pdf_url


class Elsevier_pdf_url_generator(PdfUrlGenerator):
    def __init__(self):
        PdfUrlGenerator.__init__(self)

    def get_unfinished_items(self,limit=10000):
        #从db中检索出出版社为Elsevier的article title集
        return self._get_unfinished_items(
            query_sql = "select link,google_id from articles where resource_link is null \
                  and journal_temp_info like '%Elsevier%' limit {}".format(limit)
        )

    def generate(self,unfinished_item):
        return self._generate(unfinished_item,
            google_id_index = 1,
            get_pdf_url_func = get_elsevier_pdf_url_func
        )


if __name__=='__main__':
    Elsevier_pdf_url_generator().run(thread_counts=8)
