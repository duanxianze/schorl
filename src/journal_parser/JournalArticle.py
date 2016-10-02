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

import psycopg2

class JournalArticle:
    def __init__(self,JournalObj,volume_db_id):
        self.volume_db_id = volume_db_id
        self.JournalObj = JournalObj
        self.cur = DB_CONNS_POOL.new_db_cursor()
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

    def generate_all_method(self):
        self.generate_pdf_url()
        self.generate_link()
        self.generate_abstract()
        self.generate_authors()
        self.generate_id_by_journal()
        self.generate_title()
        self.generate_year()
        self.generate_pdf_temp_url()

    @property
    def resource_type(self):
        if self.pdf_url:
            return 'PDF'

    def save_to_db(self):
        if self.save_article()=='SB':
            #重复保存
            return
        self.save_author()

    def save_author(self):
        for author_db_id in self.save_scholar_and_return_db_ids():
            self.save_scholar_article_realtion(author_db_id)
            if self.JournalObj.category_relation_cot==1:
                self.save_scholar_category_realtion(author_db_id)
                #假若该杂志社属于仅一个category，则存学者与category关系表
            if self.JournalObj.area_relation_cot==1:
                self.save_scholar_area_relation(author_db_id)
                #假若该杂志社属于仅一个area，则存学者与category关系表
                #前期检索出的都是一个area的杂志社，此处必会经过

    def save_article(self):
        '''
            注意，area_id并不存入article表,
            因为对于文章来讲，需要精确定位领域
            后期对pdf做文本挖掘，就倚仗这些专业(cateogry_id)精准的article数据,
            作为训练集得到各领域专业术语，才能确定其余article的所属专业
        '''
        if None in [self.title,self.year,self.link,self.id_by_journal]:
            print('[Error] in Save Article: Info Not Enough...')
            return
        try:
            self.cur.execute(
                'insert into articles(title,category_id,year,link,pdf_temp_url,resource_type,\
                    resource_link,summary,journal_id,id_by_journal,volume_db_id)'
                'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (self.title,self.JournalObj.category_id,self.year,self.link,self.pdf_temp_url,self.resource_type,\
                    self.pdf_url,self.abstract,self.JournalObj.sjr_id,self.id_by_journal,self.volume_db_id)
            )
            self.show_in_cmd()
        except psycopg2.IntegrityError:
            print('[Error] Article has been saved<{}> '.format(self.title))
            return 'SB'
        except Exception as e:
            print('[Error] save_article{}'.format(str(e)))

    def save_scholar(self,scholar_name):
        try:
            self.cur.execute(
                'insert into temp_scholar(name)'
                'values(%s)',
                (scholar_name.strip().replace("'",' '),)
            )
            print('[Success] Save scholar "{}" ok!'.format(scholar_name.strip().replace("'",' ')))
        except psycopg2.IntegrityError:
            print('[Error] Scholar <{}> has been saved'.format(scholar_name))
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar():{}'.format(str(e)))

    def get_scholar_db_ids(self,scholar_names):
        cur = DB_CONNS_POOL.new_db_cursor()
        sql = "select id from temp_scholar where name = '{}'"\
            .format(scholar_names[0])
        for scholar_name in scholar_names[1:]:
            if "'" in scholar_name:
                continue
            sql += " or name = '{}' ".format(scholar_name)
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        return list(map(lambda x:x[0],data))

    def save_scholar_and_return_db_ids(self):
        for author_name in self.authors:
            self.save_scholar(author_name)
        return self.get_scholar_db_ids(self.authors)

    '''
        存关于学者与三个对象的三张关系表，三个多对多关系：学者——文章，学者——大类领域，学者——小类领域
    '''

    def save_scholar_category_realtion(self,temp_scholar_id):
        '''
        if self.scholar_category_relation_is_saved(
                temp_scholar_id,category_id):
            print('[Error] The SC relation:[{},{}] has been saved'\
                  .format(temp_scholar_id,category_id))
            return
        '''
        try:
            self.cur.execute(
                'insert into temp_scholar_category(temp_scholar_id,category_id)'
                'values(%s,%s)',
                (temp_scholar_id,self.JournalObj.category_id)
            )
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar_category_realtion():{}'.format(str(e)))

    def save_scholar_area_relation(self,temp_scholar_id):
        '''
        if self.scholar_area_relation_is_saved(
                temp_scholar_id,area_id):
            print('[Error] The ScArea relation:[{},{}] has been saved'\
                  .format(temp_scholar_id,area_id))
            return
        '''
        try:
            self.cur.execute(
                'insert into temp_scholar_area(temp_scholar_id,area_id)'
                'values(%s,%s)',
                (temp_scholar_id,self.JournalObj.area_id)
            )
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar_area_realtion():{}'.format(str(e)))

    def save_scholar_article_realtion(self,temp_scholar_id):
        '''
        if self.scholar_article_relation_is_saved(temp_scholar_id):
            print('[Error] The ScArticle relation:[{},{}] has been saved'\
                  .format(temp_scholar_id,self.id_by_journal))
            return
        '''
        try:
            self.cur.execute(
                'insert into temp_scholar_article(temp_scholar_id,article_id)'
                'values(%s,%s)',
                (temp_scholar_id,self.id_by_journal)
            )
            print('[Success] Save ScArticle relation[{},{}] ok'\
                  .format(temp_scholar_id,self.id_by_journal))
        except Exception as e:
            print('[Error] in JournalArticle:save_scholar_article_realtion():{}'.format(str(e)))

    '''
        三张关于学者的关系表的独立约束检查（数据库体积增大后复杂度太高，已取消）
        关系表重复本身没啥大不了的，检查会导致阻塞的厉害
    '''

    '''
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
    '''

    def show_in_cmd(self):
        print('\n*********New article of <{}>***********'.format(self.JournalObj.name))
        '''
        if not self.pdf_url:
            print('________________________________')
            print('________________________________')
            print('________________________________')
            print('________________________________')
        '''
        print('title:\t\t{}'.format(self.title))
        print('authors:\t{}'.format(self.authors))
        print('pdf_url:\t{}'.format(self.pdf_url))
        print('pdf_temp_url:\t{}'.format(self.pdf_temp_url))
        print('link:\t\t{}'.format(self.link))
        print('id_by_journal:\t{}'.format(self.id_by_journal))
        print('volume_db_id:\t\t{}'.format(self.volume_db_id))
        print('year:\t\t\t{}'.format(self.year))
        print('category_id:\t\t{}'.format(self.JournalObj.category_id))
        print('area_id:\t\t{}'.format(self.JournalObj.area_id))
        print('abstract:\t\t{}'.format(self.abstract))
        print('*********New article of <{}>***********'.format(self.JournalObj.name))


if __name__=="__main__":
    #  Test
    from Journals_Task.JournalClass import Journal
    journalObj = Journal()
    article = JournalArticle(journalObj,volume_db_id=2)
    article.authors = ['J. Borée','P. Borsa']
    article.save_author()
    '''
    article.authors = ['gelin','sbxgl']
    article.id_by_journal = 'xxx'
    article.category_id = 1
    article.title = 'woshishabiha'
    article.pdf_url = 'xxxx.pdf'
    article.link = 'www.dsdsd.com'
    article.year = 20111
    article.save_to_db()
    '''
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