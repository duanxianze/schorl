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
    def __init__(self,JournalObj):
        self.JournalObj = JournalObj
        self.journal_id = JournalObj.sjr_id
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
        print('save_to_db{}'.format(self.title))
        '''
        self.save_article()
        self.save_scholar()
        self.save_scholar_article_realtion()
        if self.JournalObj.category_relation_cot==1:
            self.save_scholar_category_realtion()
            #假若该杂志社属于仅一个category，则存学者与category关系表
        if self.JournalObj.area_relation_cot==1:
            self.save_scholar_article_realtion()
            #假若该杂志社属于仅一个area，则存学者与category关系表
            #前期检索出的都是一个area的杂志社，此处必会经过
        '''

    def save_article(self):
        try:
            self.cur.execute(
                'insert into articles(title,year,link,\
                    resource_type,resource_link,summary,journal_id,id_by_journal)'
                'values(%s,%s,%s,%s,%s,%s,%s,%s)',
                (self.title,self.year,self.link,self.resource_type,\
                    self.pdf_url,self.abstract,self.journal_id,self.id_by_journal)
            )
            print('save article ok!')
            return True
        except Exception as e:
            print('[Error] in JournalArticle:save_article():\n{}'.format(str(e)))
        return False

    def save_scholar(self,scholar_name):
        try:
            self.cur.execute(
                'insert into temp_scholar(name)'
                'values(%s)',
                (scholar_name)
            )
            print('save scholar ok!')
            return True
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar():\n{}'.format(str(e)))
        return False

    def get_scholar_db_id(self,scholar_name):
        self.cur.execute(
            "select id from temp_scholar where name = '{}'"\
                .format(scholar_name)
        )
        return self.cur.fetchall()[0][0]

    def save_scholar_and_return_db_ids(self):
        scholar_db_ids = []
        for author_name in self.authors:
            self.save_scholar(author_name)
            scholar_db_id = self.get_scholar_db_id(author_name)
            scholar_db_ids.append(scholar_db_id)
        return scholar_db_ids

    def get_category_ids_by_journal_id(self,journal_id):
        cur = new_db_cursor()
        cur.execute(
            'select category_id from journal_category \
            where journal_id={}'.format(journal_id)
        )
        data = cur.fetchall()
        cur.close()
        return data

    def save_scholar_category_realtion(self,temp_scholar_id,category_id):
        try:
            self.cur.execute(
                'insert into temp_scholar_category(temp_scholar_id,category_id)'
                'values(%s,%s)',
                (temp_scholar_id,category_id)
            )
            return True
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar_category_realtion():\n{}'.format(str(e)))
        return False

    def save_scholar_article_realtion(self,temp_scholar_id):
        try:
            self.cur.execute(
                'insert into temp_scholar_article(temp_scholar_id,article_id)'
                'values(%s,%s)',
                (temp_scholar_id,self.id_by_journal)
            )
            return True
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar_article_realtion():\n{}'.format(str(e)))
        return False

    def scholar_category_relation_is_saved(self,temp_scholar_id,category_id):
        cur = new_db_cursor()
        cur.execute(
            'select count(*) from temp_scholar_category\
            where temp_scholar_id={} and category_id={}'\
                .format(temp_scholar_id,category_id)
        )
        data = cur.fetchall[0][0]
        print('SC amount',data)
        cur.close()
        return data

    def scholar_article_relation_is_saved(self,temp_scholar_id):
        cur = new_db_cursor()
        cur.execute(
            'select count(*) from temp_scholar_article\
            where temp_scholar_id={} and category_id={}'\
                .format(temp_scholar_id,self.id_by_journal)
        )
        data = cur.fetchall[0][0]
        print('SA amount',data)
        cur.close()
        return data

    def show_in_cmd(self):
        print('\n*********New article of <{}>***********'.format(self.JournalObj.publisher))
        print('title:\t\t{}'.format(self.title))
        print('abstract:\t\t{}'.format(self.abstract))
        print('pdf_url:\t{}'.format(self.pdf_url))
        print('authors:\t{}'.format(self.authors))
        print('link:\t\t{}'.format(self.link))
        print('id_by_journal:\t{}'.format(self.id_by_journal))
        print('year:\t\t{}'.format(self.year))
        print('*********New article of <{}>***********'.format(self.JournalObj.publisher))