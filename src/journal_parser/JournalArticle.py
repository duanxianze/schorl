#coding:utf-8
"""
@file:      JournalArticle.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-19 11:25
@description:
        The basic class of article from kinds of journals
"""
from src.db_config import new_db_cursor


class JournalArticle:
    def __init__(self,journal_id):
        self.journal_id = journal_id
        self.cur = new_db_cursor()
        self.title = None
        self.abstract = None
        self.pdf_url = None
        self.authors = None
        self.link = None
        self.id_by_journal = None
        self.year = None

    def generate_title(self):
        pass

    def generate_authors(self):
        pass

    def generate_link(self):
        pass

    def generate_abstract(self):
        pass

    def generate_year(self):
        pass

    def generate_pdf_url(self):
        pass

    def generate_id_by_journal(self):
        pass

    def generate_all_method(self):
        self.generate_pdf_url()
        self.generate_link()
        self.generate_abstract()
        self.generate_authors()
        self.generate_id_by_journal()
        self.generate_title()
        self.generate_year()

    @property
    def resource_type(self):
        if self.pdf_url:
            return 'PDF'

    def save_to_db(self):
        if self.save_article():
            if self.save_scholar():
                self.save_scholar_category_realtion()

    def save_article(self):
        self.cur.execute(
            'insert into articles(title,year,link,\
                resource_type,resource_link,summary,journal_id,id_by_journal)'
            'values(%s,%s,%s,%s,%s,%s,%s,%s)',
            (self.title,self.year,self.link,self.resource_type,\
                self.pdf_url,self.abstract,self.journal_id,self.id_by_journal)
        )

    def save_scholar(self):
        self.cur.execute(
            ''
        )

    def save_scholar_category_realtion(self):
        pass

    def save_scholar_article_realtion(self):
        pass

    def scholar_category_relation_is_saved(self):
        pass

    def show_in_cmd(self):
        print('title:\t{}'.format(self.title))
        print('abstract:\t{}'.format(self.abstract))
        print('pdf_url:\t{}'.format(self.pdf_url))
        print('authors:\t{}'.format(self.authors))
        print('link:\t{}'.format(self.link))
        print('id_by_journal:\t{}'.format(self.id_by_journal))
        print('year:\t{}'.format(self.year))