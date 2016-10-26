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

from crawl_tools.Timer import get_beijing_time
from crawl_tools.request_with_proxy import request_with_random_ua,request_with_proxy
from db_config import REMOTE_CONNS_POOL
import psycopg2,time,random
from crawl_tools.decorators import except_pass,except_return_none
from multiprocessing.dummy import Pool as ThreadPool

EP_METHOD = lambda func:except_pass(func,'JournalSpider')
ERN_METHOD = lambda func:except_return_none(func,'JournalSpider')

class JournalSpider:
    def __init__(self,JournalObj):
        self.JournalObj = JournalObj
        self.volume_links = []

    def generate_volume_links(self):
        pass

    @EP_METHOD
    def _run(self,AllItemsPageParser,JournalArticle,use_tor=False,
             check_pdf_url=True,internal_thread_cot=8,just_init=False):
        self.just_init = just_init
        volume_items = list(set(
            self.get_unfinished_volume_links()
        ))
        random.shuffle(volume_items)
        params_dict = {
            'AllItemsPageParser':AllItemsPageParser,
            'JournalArticle':JournalArticle,
            'use_tor':use_tor,
            'check_pdf_url':check_pdf_url,
        }
        params_dicts = []
        for volume_item in volume_items:
            params_dict['volume_item'] = volume_item
            new_dict = {}
            for key in params_dict.keys():
                new_dict[key] = params_dict[key]
            params_dicts.append(new_dict)
        pool = ThreadPool(internal_thread_cot)
        for params_dict in params_dicts:
            print(params_dict['volume_item'])
        result_list = pool.map(self.crawl_vp,params_dicts)
        print('Results List = {}'.format(result_list))
        AllVolumesOK = False not in result_list
        if AllVolumesOK and volume_items:
            self.mark_journal_ok()
        pool.close()
        pool.join()

    @ERN_METHOD
    def crawl_vp(self,params_dict):
        return self.crawl_volume_page(
            volume_item = params_dict['volume_item'],
            AllItemsPageParser = params_dict['AllItemsPageParser'],
            JournalArticle = params_dict['JournalArticle'],
            use_tor = params_dict['use_tor'],
            check_pdf_url = params_dict['check_pdf_url'],
        )

    def handle_volume_link_for_multi_results(self,volume_link):
        #对多页的支持，根据不同出版社各自情况，可能需要加一些ajax参数
        return volume_link

    @ERN_METHOD
    def crawl_volume_page(self,volume_item,AllItemsPageParser,
                JournalArticle,use_tor=False,check_pdf_url=True):
        volume_link = self.handle_volume_link_for_multi_results(volume_item[0])
        volume_db_id = volume_item[1]
        if use_tor:
            #此情况属于完全不可能直接获取pdf_url时使用，用远程服务器加速
            html_source = request_with_proxy(volume_link).text
        else:
            html_source = request_with_random_ua(volume_link).text
        parser = AllItemsPageParser(html_source)
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
        if self.crawl_articles(sections,volume_year,
                volume_db_id,JournalArticle,check_pdf_url)==False:
            return False
        if len(parser.sections)>0:
            self.mark_volume_ok(volume_db_id)
            return True
        return False

    @ERN_METHOD
    def crawl_articles(self,sections,volume_year,
            volume_db_id,JournalArticle,check_pdf_url=True):
        pdf_url_null_cot = 0
        for sec in sections:
            params = [sec,self.JournalObj,volume_db_id]
            if volume_year:
                params.append(volume_year)
            try:
                article = JournalArticle(*params)
            except Exception as e:
                print('[Error] JournalSpider:JournalArticle Init:{}'\
                      .format(str(e)))
                continue
            if check_pdf_url:
                if article.pdf_url==None and article.pdf_temp_url==None:
                    pdf_url_null_cot += 1
                else:
                    pdf_url_null_cot = 0
                if pdf_url_null_cot>3:
                    return False
            if article.authors in ([''],[]):
                print('[Error] JournalSpider:\
                    No authors in article <{}>'.format(article.title))
                continue
            article.save_to_db()

    @EP_METHOD
    def mark_journal_ok(self):
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        cur.execute(
            'update journal set is_crawled_all_article = true\
             where sjr_id = {}'.format(self.JournalObj.sjr_id)
        )
        cur.close()

    @ERN_METHOD
    def get_db_volume_item(self,volume_link):
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        cur.execute(
            "select is_crawled from journal_volume \
                where link = '{}' ".format(volume_link)
        )
        data = cur.fetchall()
        cur.close()
        return data

    @EP_METHOD
    def create_volume(self,volume_link):
        try:
            cur = REMOTE_CONNS_POOL.new_db_cursor()
            cur.execute(
                "insert into journal_volume(link,journal_sjr_id,is_crawled,create_time)"
                "values(%s,%s,%s,%s)",
                (volume_link,self.JournalObj.sjr_id,False,get_beijing_time())
            )
            print('[Success]Save ok volume_link: {} !'.format(volume_link))
        except psycopg2.IntegrityError as e:
            print('[Error] in volume_link create:\n{} '.format(str(e)))
        except psycopg2.OperationalError as e:
            print('[Error] in volume_link create:\nserver conn error{}'.format(str(e)))
        cur.close()

    @EP_METHOD
    def mark_volume_ok(self,volume_db_id):
        sql = "update journal_volume set is_crawled=true \
                where id={}".format(volume_db_id)
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        cur.execute(sql)
        cur.close()
        print('Mark volume {} ok!'.format(volume_db_id))

    @EP_METHOD
    def create_new_volumes(self):
        print('Init volume_links of {}...'.format(self.JournalObj.name))
        if self.volume_links==[]:
            return
        for volume_link in self.volume_links:
            self.create_volume(volume_link)
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        cur.execute(
            'update journal set volume_links_got=TRUE \
              where sjr_id={}'.format(self.JournalObj.sjr_id)
        )
        cur.close()
        print(' volume links created ok! <{}>'.\
              format(self.JournalObj.name))

    @ERN_METHOD
    def get_unfinished_volume_links(self):
        if not self.JournalObj.volume_links_got:
            #第一次初始化
            self.create_new_volumes()
        if self.just_init:
            return []
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select link,id from journal_volume \
              where journal_sjr_id={} and is_crawled=FALSE'\
                .format(self.JournalObj.sjr_id)
        )
        return cur.fetchall()
