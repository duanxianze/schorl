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
        self.write_cur = REMOTE_CONNS_POOL.new_db_cursor()

    def _run(self,AllItemsPageParser,JournalArticle):
        volume_items = list(set(
            self.get_unfinished_volume_links()
        ))
        random.shuffle(volume_items)
        AllVolumesOK = True
        for volume_item in volume_items:
            if not self.crawl_volume_page(
                volume_item,AllItemsPageParser,JournalArticle):
                AllVolumesOK = False
        if AllVolumesOK:
            self.mark_journal_ok()

    def crawl_volume_page(self,volume_item,AllItemsPageParser,JournalArticle):
        volume_link = volume_item[0]
        volume_db_id = volume_item[1]
        parser = AllItemsPageParser(
            html_source = request_with_random_ua(volume_link).text
        )
        try:
            sections = parser.sections
        except Exception as e:
            print('[Error] JournalSpider:Page Invalid {}\n\
                error_url {}'.format(str(e),volume_link))
            return False
        try:
            volume_year = parser.volume_year
            print('Volume_year:{}'.format(volume_year))
        except AttributeError:
            volume_year = None
        print('\nPage Url: %s '%volume_link)
        self.crawl_articles(sections,volume_year,volume_db_id,JournalArticle)
        if len(parser.sections)>0:
            self.mark_volume_ok(volume_db_id)
            return True
        return False

    def crawl_articles(self,sections,volume_year,volume_db_id,JournalArticle):
        for sec in sections:
            params = [sec,self.JournalObj,volume_db_id]
            if volume_year:
                params.append(volume_year)
            try:
                article = JournalArticle(*params)
            except Exception as e:
                print('[Error] JournalSpider:\
                    JournalArticle Init:{}'.format(str(e)))
                return False
            if article.authors in ([''],[]):
                print('[Error] JournalSpider:\
                    No authors in article <{}>'.format(article.title))
                continue
            article.save_to_db()

    def mark_journal_ok(self):
        self.write_cur.execute(
            'update journal set is_crawled_all_article = true\
             where sjr_id = {}'.format(self.JournalObj.sjr_id)
        )

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
        try:
            self.write_cur.execute(
                "insert into journal_volume(link,journal_sjr_id,is_crawled)"
                "values(%s,%s,%s)",
                (volume_link,self.JournalObj.sjr_id,False)
            )
            print('[Success]Save ok volume_link: {} !'.format(volume_link))
        except psycopg2.IntegrityError as e:
            print('[Error] in volume_link create:\n{} '.format(str(e)))
        except psycopg2.OperationalError as e:
            print('[Error] in volume_link create:\nserver conn error{}'.format(str(e)))

    def mark_volume_ok(self,volume_db_id):
        sql = "update journal_volume set is_crawled=true \
                where id={}".format(volume_db_id)
        #print(sql)
        self.write_cur.execute(sql)
        print('Mark volume {} ok!'.format(volume_db_id))

    def create_new_volumes(self):
        print('Init volume_links of {}...'.format(self.JournalObj.name))
        for volume_link in self.volume_links:
            self.create_volume(volume_link)
        self.write_cur.execute(
            'update journal set volume_links_got=TRUE \
              where sjr_id={}'.format(self.JournalObj.sjr_id)
        )

    def get_unfinished_volume_links(self):
        if not self.JournalObj.volume_links_got:
            #第一次初始化
            self.create_new_volumes()
            return self.volume_links
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select link,id from journal_volume \
              where journal_sjr_id={} and is_crawled=FALSE'\
                .format(self.JournalObj.sjr_id)
        )
        data = cur.fetchall()
        cur.close()
        return data

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    JournalObj=Journal()
    JournalObj.site_source = 'http://www.elsevier.com/wps/find/journaldescription.cws_home/505606/description#description'
    JournalObj.sjr_id = 1
    js = JournalSpider(JournalObj)
    js.mark_volume_ok('www.xxxx.com')
    #js.create_volume(volume_link='www.xxxx.com')