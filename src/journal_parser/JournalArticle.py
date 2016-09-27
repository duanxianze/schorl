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
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)
from db_config import DB_CONNS_POOL

class JournalArticle:
    def __init__(self,JournalObj):
        self.JournalObj = JournalObj
        self.journal_id = JournalObj.sjr_id
        self.cur = DB_CONNS_POOL.new_db_cursor()
        self.category_id = None
        self.area_id = None
        self.title = None
        self.abstract = None
        self.pdf_url = None
        self.pdf_temp_url = None
        self.authors = []
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

    def generate_pdf_temp_url(self):
        pass

    def generate_id_by_journal(self):
        pass

    def generate_category_id(self):
        if self.JournalObj.category_relation_cot == 1:
            ids = self.get_category_ids_by_journal_id(
                journal_id=self.journal_id
            )
            #print(ids)
            self.category_id = ids[0][0]

    def generate_area_id(self):
        if self.JournalObj.area_relation_cot == 1:
            ids = self.get_area_ids_by_journal_id(
                journal_id=self.journal_id
            )
            #print(ids)
            self.area_id = ids[0][0]

    def generate_all_method(self):
        self.generate_pdf_url()
        self.generate_link()
        self.generate_abstract()
        self.generate_authors()
        self.generate_id_by_journal()
        self.generate_title()
        self.generate_year()
        self.generate_category_id()
        self.generate_area_id()
        self.generate_pdf_temp_url()

    @property
    def resource_type(self):
        if self.pdf_url:
            return 'PDF'

    def save_to_db(self):
        self.save_article()
        for author_db_id in self.save_scholar_and_return_db_ids():
            self.save_scholar_article_realtion(author_db_id)
            if self.JournalObj.category_relation_cot==1:
                self.update_article_category_id()
                self.save_scholar_category_realtion(author_db_id)
                #假若该杂志社属于仅一个category，则存学者与category关系表
            if self.JournalObj.area_relation_cot==1:
                self.save_scholar_area_relation(author_db_id)
                #假若该杂志社属于仅一个area，则存学者与category关系表
                #前期检索出的都是一个area的杂志社，此处必会经过

    def update_article_category_id(self):
        try:
            self.cur.execute(
                "update articles set category_id={} where id_by_journal='{}' "\
                    .format(self.category_id,self.id_by_journal)
            )
        except Exception as e:
            print('[Error] Article category_id Update:{}'.format(str(e)))

    def save_article(self):
        if self.is_saved:
            print('[Error] Article <{}> already saved before'\
                  .format(self.title))
            return
        try:
            self.cur.execute(
                'insert into articles(title,year,link,pdf_temp_url,\
                    resource_type,resource_link,summary,journal_id,id_by_journal)'
                'values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (self.title,self.year,self.link,self.pdf_temp_url,self.resource_type,\
                    self.pdf_url,self.abstract,self.journal_id,self.id_by_journal)
            )
            self.show_in_cmd()
        except Exception as e:
            print('[Error] in JournalArticle:save_article():\n{}'.format(str(e)))

    @property
    def is_saved(self):
        cur = DB_CONNS_POOL.new_db_cursor()
        cur.execute(
            "select count(*) from articles where id_by_journal='{}'"\
                .format(self.id_by_journal)
        )
        data = cur.fetchall()[0][0]
        cur.close()
        return data

    def save_scholar(self,scholar_name):
        if self.get_scholar_db_id(scholar_name):
            print('[Error] The author: <{}> has been saved'\
                  .format(scholar_name))
            return
        try:
            self.cur.execute(
                'insert into temp_scholar(name)'
                'values(%s)',
                (scholar_name,)
            )
            print('[Success] Save scholar "{}" ok!'.format(scholar_name.strip()))
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar():\n\t{}'.format(str(e)))

    def get_scholar_db_id(self,scholar_name):
        cur = DB_CONNS_POOL.new_db_cursor()
        cur.execute(
            "select id from temp_scholar "
            "where name = %s",
            (scholar_name,)
        )
        data = cur.fetchall()
        cur.close()
        return data

    def save_scholar_and_return_db_ids(self):
        scholar_db_ids = []
        for author_name in self.authors:
            self.save_scholar(author_name)
            scholar_db_id = self.get_scholar_db_id(author_name)[0][0]
            scholar_db_ids.append(scholar_db_id)
        return scholar_db_ids

    def get_category_ids_by_journal_id(self,journal_id):
        cur = DB_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select category_id from journal_category \
            where journal_id={}'.format(journal_id)
        )
        data = cur.fetchall()
        cur.close()
        return data

    def get_area_ids_by_journal_id(self,journal_id):
        cur = DB_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select area_id from journal_area \
            where journal_id={}'.format(journal_id)
        )
        data = cur.fetchall()
        cur.close()
        return data

    def save_scholar_category_realtion(self,temp_scholar_id):
        if not self.category_id:
            print('[Error] SC Realtion saved error:\n\t Category_id cant be null')
        if self.scholar_category_relation_is_saved(
                temp_scholar_id,self.category_id):
            print('[Error] The SC relation:[{},{}] has been saved'\
                  .format(temp_scholar_id,self.category_id))
        try:
            self.cur.execute(
                'insert into temp_scholar_category(temp_scholar_id,category_id)'
                'values(%s,%s)',
                (temp_scholar_id,self.category_id)
            )
            return True
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar_category_realtion():\n\t{}'.format(str(e)))
        return False

    def save_scholar_area_relation(self,temp_scholar_id):
        if not self.area_id:
            print('[Error] SchArea Realtion saved error:\n\t Area_id cant be null')
        if self.scholar_area_relation_is_saved(
                temp_scholar_id,self.area_id):
            print('[Error] The ScArea relation:[{},{}] has been saved'\
                  .format(temp_scholar_id,self.area_id))
        try:
            self.cur.execute(
                'insert into temp_scholar_area(temp_scholar_id,area_id)'
                'values(%s,%s)',
                (temp_scholar_id,self.area_id)
            )
            return True
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar_area_realtion():\n\t{}'.format(str(e)))
        return False

    def save_scholar_article_realtion(self,temp_scholar_id):
        if self.scholar_article_relation_is_saved(temp_scholar_id):
            print('[Error] The ScArticle relation:[{},{}] has been saved'\
                  .format(temp_scholar_id,self.id_by_journal))
            return
        try:
            self.cur.execute(
                'insert into temp_scholar_article(temp_scholar_id,article_id)'
                'values(%s,%s)',
                (temp_scholar_id,self.id_by_journal)
            )
            print('[Success] Save ScArticle relation[{},{}] ok'\
                  .format(temp_scholar_id,self.id_by_journal))
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar_article_realtion():\n\t{}'.format(str(e)))

    def scholar_category_relation_is_saved(self,temp_scholar_id,category_id):
        cur = DB_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select count(*) from temp_scholar_category\
            where temp_scholar_id={} and category_id={}'\
                .format(temp_scholar_id,category_id)
        )
        data = cur.fetchall()[0][0]
        #print('SC amount',data)
        cur.close()
        return data

    def scholar_area_relation_is_saved(self,temp_scholar_id,area_id):
        cur = DB_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select count(*) from temp_scholar_area\
            where temp_scholar_id={} and area_id={}'\
                .format(temp_scholar_id,area_id)
        )
        data = cur.fetchall()[0][0]
        cur.close()
        return data

    def scholar_article_relation_is_saved(self,temp_scholar_id):
        cur = DB_CONNS_POOL.new_db_cursor()
        cur.execute(
            "select count(*) from temp_scholar_article\
            where temp_scholar_id={} and article_id='{}'"\
                .format(temp_scholar_id,self.id_by_journal)
        )
        data = cur.fetchall()[0][0]
        #print('SA amount',data)
        cur.close()
        return data

    def show_in_cmd(self):
        print('\n*********New article of <{}>***********'.format(self.JournalObj.name))
        print('title:\t\t{}'.format(self.title))
        print('authors:\t{}'.format(self.authors))
        print('pdf_url:\t{}'.format(self.pdf_url))
        print('pdf_temp_url:\t{}'.format(self.pdf_temp_url))
        print('link:\t\t{}'.format(self.link))
        print('id_by_journal:\t{}'.format(self.id_by_journal))
        print('year:\t\t\t{}'.format(self.year))
        print('category_id:\t\t{}'.format(self.category_id))
        print('area_id:\t\t{}'.format(self.area_id))
        print('abstract:\t\t{}'.format(self.abstract))
        print('*********New article of <{}>***********'.format(self.JournalObj.name))


if __name__=="__main__":
    #  Test
    from Journals_Task.JournalClass import Journal
    journalObj = Journal()
    article = JournalArticle(journalObj)
    article.authors = ['gelin','sbxgl']
    article.id_by_journal = 'xxx'
    article.category_id = 1
    article.title = 'woshishabiha'
    article.pdf_url = 'xxxx.pdf'
    article.link = 'www.dsdsd.com'
    article.year = 20111
    article.save_to_db()
    '''
    scholar_id = article.get_scholar_db_id('tony')
    print(scholar_id)
    article.save_scholar(scholar_name='luyang')
    ids = article.save_scholar_and_return_db_ids()
    print(ids)
    article.save_scholar_article_realtion(temp_scholar_id=2)
    article.scholar_category_relation_is_saved(temp_scholar_id=2,category_id=1)
    article.save_scholar_category_realtion(temp_scholar_id=2)
    article.get_category_ids_by_journal_id()
    '''