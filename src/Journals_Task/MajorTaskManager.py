#coding:utf-8
"""
@file:      MajorTaskManager.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-18 0:01
@description:
            特定领域下的杂志爬虫任务启动模块，调度数据库和爬虫
"""
from src.Journals_Task.ExistedSpiders import *
from src.Journals_Task.GetMajorJournals import MajorEntrance
from multiprocessing.dummy import Pool as ThreadPool
from src.Journals_Task.JournalClass import Journal

class MajorTaskManager:
    def __init__(self,majorKeyword):
        self.majorKeyword = majorKeyword

    def get_journals_info_dict(self,
        single_area_relation = True,
        index_by_area = False,
        index_by_category = True
    ):
        return MajorEntrance(
            major_keyword = self.majorKeyword
        ).get_possible_journals(
            single_area_relation=single_area_relation,
            index_by_area=index_by_area,
            index_by_category=index_by_category
        )

    def get_task_spider(self,spiders_infos,journal_url):
        for spider_info in spiders_infos:
            if spider_info['publisherKeyword'] in journal_url:
                return spider_info['publisherSpiderClass']
        return None

    def launch_journal_spider(self,db_journal_item):
        JournalObj = Journal()
        JournalObj.name = db_journal_item[0]
        JournalObj.sjr_id = db_journal_item[1]
        JournalObj.site_source = db_journal_item[2]
        JournalObj.area_relation_cot = db_journal_item[3]
        JournalObj.category_relation_cot = db_journal_item[4]
        #print(journal_name,journal_sjr_id,journal_url)
        spider = self.get_task_spider(EXISTED_SPIDERS,JournalObj.site_source)
        if spider:
            print('[{}]: Got Task of <{}> ( {} )'.\
                  format(spider.__name__,JournalObj.name,JournalObj.site_source))
            spider(JournalObj).run()
        else:
            print('[Spider Not Found]: <{}> 所属出版社解析器未找到( {} )'\
                  .format(JournalObj.name,JournalObj.site_source))

    def run(
            self,journal_need_single_area_relation = True,
            journal_need_index_by_area = False,
            journal_need_index_by_category = True,
            thread_cot = 16
        ):
        thread_pool = ThreadPool(thread_cot)
        journals_info_dict = self.get_journals_info_dict(
            single_area_relation = journal_need_single_area_relation,
            index_by_area = journal_need_index_by_area,
            index_by_category = journal_need_index_by_category
        )
        for key in journals_info_dict.keys():
            category_name = key
            journal_items = journals_info_dict[key]
            print(category_name,journal_items)
            thread_pool.map(self.launch_journal_spider,journal_items)


if __name__=="__main__":
    #为使远程数据库传输压力变小，建议选择比较精细的领域关键词
    MajorTaskManager(majorKeyword = 'Artificial').run(
        journal_need_single_area_relation = True,
        journal_need_index_by_area = False,
        journal_need_index_by_category = True,
        thread_cot = 16
    )