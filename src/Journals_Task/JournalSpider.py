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

from crawl_tools.request_with_proxy import request_with_random_ua
from db_config import REMOTE_CONNS_POOL
import psycopg2,time,random

class JournalSpider:
    def __init__(self,JournalObj):
        self.JournalObj = JournalObj
        self.volume_links = []

    def crawl_volume_page(self,volume_link,AllItemsPageParser,JournalArticle):
        parser = AllItemsPageParser(
            html_source = request_with_random_ua(volume_link).text
        )
        try:
            sections = parser.sections
        except Exception as e:
            print('[Error] Page Invalid in first check{}\nerror_url {}'\
                  .format(str(e),volume_link))
            return
        try:
            volume_year = parser.volume_year
            print('volume_year:{}'.format(volume_year))
        except Exception as e:
            print('Volume year is none:{}'.format(str(e)))
            volume_year = None
        print('\nPage Url: %s '%volume_link)
        #print('len(sections)',len(sections))
        for sec in sections:
            if volume_year is not None:
                '''
                article = JournalArticle(sec,self.JournalObj,volume_year)
                '''
                try:
                    article = JournalArticle(sec,self.JournalObj,volume_year)
                except Exception as e:
                    print('[Error]JournalSpider:crawl_volume_page:%s'%str(e))
                    return
            else:
                '''
                article = JournalArticle(sec,self.JournalObj)
                '''
                try:
                    article = JournalArticle(sec,self.JournalObj)
                except Exception as e:
                    print('[Error]JournalSpider:crawl_volume_page:%s'%str(e))
                    return

            if not article.authors:
                print('[Error] No authors in article <{}>'.format(article.title))
                continue
            while(1):
                try:
                    article.save_to_db()
                    break
                except psycopg2.OperationalError:
                    print('db error,again')
                    time.sleep(2)
        if len(parser.sections)>0:
                print(len(parser.sections))
                self.mark_volume_ok(volume_link)

    def _run(self,AllItemsPageParser,JournalArticle):
        volume_links = list(set(
            self.get_unfinished_volume_links()
        ))
        random.shuffle(volume_links)
        for volume_link in volume_links:
            self.crawl_volume_page(
                volume_link,AllItemsPageParser,JournalArticle)
        if len(volume_links)>0:
            self.mark_journal_ok()

    def mark_journal_ok(self):
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        cur.execute(
            'update journal set is_crawled_all_article = true\
             where sjr_id = {}'.format(self.JournalObj.sjr_id)
        )
        cur.close()

    def get_db_volume_item(self,volume_link):
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        cur.execute(
            "select is_crawled from journal_volume \
                where link = '{}' ".format(volume_link)
        )
        data = cur.fetchall()
        cur.close()
        return data

    def create_volume(self,volume_link):
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        try:
            cur.execute(
                "insert into journal_volume(link,journal_sjr_id,is_crawled)"
                "values(%s,%s,%s)",
                (volume_link,self.JournalObj.sjr_id,False)
            )
            print('[Success]Save ok volume_link: {} !'.format(volume_link))
        except psycopg2.IntegrityError as e:
            print('[Error] in volume_link create:\n{} '.format(str(e)))
        except psycopg2.OperationalError as e:
            print('[Error] in volume_link create:\nserver conn error{}'.format(str(e)))
        cur.close()

    @property
    def saved_volumes_amount_of_journal(self):
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select count(*) from journal_volume \
              where journal_sjr_id={}'.format(self.JournalObj.sjr_id)
        )
        data = cur.fetchall()[0][0]
        cur.close()
        return data

    def mark_volume_ok(self,volume_link):
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        sql = "update journal_volume set is_crawled=true \
                where link='{}'".format(volume_link)
        #print(sql)
        cur.execute(sql)
        print('Mark volume {} ok!'.format(volume_link))

    def create_new_volumes(self):
        print('Init volume_links of {}...'.format(self.JournalObj.name))
        for volume_link in self.volume_links:
            self.create_volume(volume_link)
        if self.saved_volumes_amount_of_journal>10:
            cur = REMOTE_CONNS_POOL.new_db_cursor()
            cur.execute(
                'update journal set volume_links_got=TRUE \
                  where sjr_id={}'.format(self.JournalObj.sjr_id)
            )
            cur.close()

    def get_unfinished_volume_links(self):
        if not self.JournalObj.volume_links_got:
            #第一次初始化
            self.create_new_volumes()
            return self.volume_links
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select link from journal_volume \
              where journal_sjr_id={} and is_crawled=FALSE'\
                .format(self.JournalObj.sjr_id)
        )
        data = cur.fetchall()
        cur.close()
        return list(map(
            lambda x:x[0],data
        ))

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    JournalObj=Journal()
    JournalObj.site_source = 'http://www.elsevier.com/wps/find/journaldescription.cws_home/505606/description#description'
    JournalObj.sjr_id = 1
    js = JournalSpider(JournalObj)
    js.mark_volume_ok('www.xxxx.com')
    #js.create_volume(volume_link='www.xxxx.com')