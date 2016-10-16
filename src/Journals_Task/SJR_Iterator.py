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
    def __init__(self,publisher_keyword=None,driver_pool_size=0):
        self.urls = SJR_Searcher(publisher_keyword).urls
        self.driver_pool_size = driver_pool_size
        if publisher_keyword:
            self.crawl_all = False
        else:
            self.crawl_all = True
            if driver_pool_size>0:
                self.drivers = DriversPool(
                    size=driver_pool_size,visual=True
                )

    def crawl_per_page_result(self,url):
        print(url)
        if self.crawl_all:
            if self.driver_pool_size>0:
                driverObj = self.drivers.get_one_free_driver()
                drvier = driverObj.engine
            else:
                drvier = None
            try:
                parser = RankPageParser(url,drvier)
            except Exception as e:
                print(str(e))
            try:
                driverObj.status = 'free'
            except:
                pass
            JournalItem = RankJournal
        else:
            html_source = request_with_random_ua(url).text
            parser = SearchPageParser(html_source)
            JournalItem = PublisherJournal
        print(len(parser.sections))
        for sec in parser.sections:
            JournalItem(sec).save_to_db()

    def run(self,thread_count=16):
        pool = ThreadPool(thread_count)
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
        pool = ThreadPool(64)
        pool.map(self.crawl_per_item,self.db_items)
        pool.close()
        pool.join()


if __name__=="__main__":
    '''
    from crawl_tools.WatchDog import close_procs_by_keyword
    close_procs_by_keyword('chromedriver')
    close_procs_by_keyword('phantom')
    SJR_Iterator(publisher_keyword=None).run(thread_count=64)
    '''
    SJR_Updater().run()



