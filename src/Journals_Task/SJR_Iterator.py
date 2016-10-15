#coding:utf-8
"""
@file:      SJR_Iterator
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-15 18:51
@description:
            用于迭代采购SJR网站上关于某publisher(或全库)完全版本的journal magazine信息
"""
from journal_parser.SJR_Parser import SJR_Searcher,SearchPageParser\
    ,PublisherJournal,RankPageParser,RankJournal,JournalDetailPageParser
from crawl_tools.request_with_proxy import request_with_random_ua
from multiprocessing.dummy import Pool as ThreadPool
from db_config import DB_CONNS_POOL
from crawl_tools.DriversPool import DriversPool

class SJR_Iterator:
    def __init__(self,publisher_keyword=None):
        self.urls = SJR_Searcher(publisher_keyword).urls
        if publisher_keyword:
            self.crawl_all = False
        else:
            self.crawl_all = True
            self.drivers = DriversPool(size=8,visual=True)

    def crawl_per_page_result(self,url):
        print(url)
        if self.crawl_all:
            driver = self.drivers.get_one_free_driver()
            try:
                parser = RankPageParser(driver)
            except Exception as e:
                print(str(e))
            driver.status = 'free'
            JournalItem = RankJournal
        else:
            html_source = request_with_random_ua(url).text
            parser = SearchPageParser(html_source)
            JournalItem = PublisherJournal
        print(len(parser.sections))
        for sec in parser.sections:
            JournalItem(sec).show_in_cmd()

    def run(self):
        pool = ThreadPool(16)
        pool.map(self.crawl_per_page_result,self.urls)
        pool.close()
        pool.join()


class SJR_Updater:
    def __init__(self):
        pass

    @property
    def db_items(self):
        cur = DB_CONNS_POOL.new_db_cursor()
        cur.execute(
            'select sjr_id from journal where country is null'
        )
        data = cur.fetchall()
        cur.close()
        return list(map(
            lambda x:x[0],data
        ))

    def crawl_per_item(self,sjr_id):
        try:
            journal = JournalDetailPageParser(sjr_id)
            journal.save_new_info()
            journal.show_in_cmd()
        except Exception as e:
            print(str(e))

    def run(self):
        pool = ThreadPool(32)
        pool.map(self.crawl_per_item,self.db_items)
        pool.close()
        pool.join()


if __name__=="__main__":
    SJR_Iterator(publisher_keyword=None).run()
    #SJR_Updater().run()



