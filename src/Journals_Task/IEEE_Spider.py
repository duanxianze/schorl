#coding:utf-8
"""
@file:      IEEE_Spider.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-17 19:55
@description:
            ??
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from Journals_Task.JournalSpider import JournalSpider
from journal_parser.IEEE_Parser import IEEE_AllItemsPageParser,IEEE_Article
from crawl_tools.request_with_proxy import request_with_random_ua


class IEEE_Spider(JournalSpider):
    '''
       sample_url: http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=5480&punumber=83
    '''
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.JournalObj = JournalObj

    def run(self):
        for volume_link in IEEE_AllItemsPageParser(
            html_source = request_with_random_ua(self.url).text
        ).volume_links:
            print(volume_link)
            parser = IEEE_AllItemsPageParser(
                html_source = request_with_random_ua(volume_link).text
            )
            for sec in parser.sections:
                article = IEEE_Article(sec,self.JournalObj,parser.volume_year)
                if article.title_text_span==None:
                    continue
                article.save_to_db()
        self.mark_journal_ok()


if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    from crawl_tools.DriversPool import Driver
    JournalObj=Journal()
    JournalObj.site_source = 'http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=5480&punumber=83'
    JournalObj.sjr_id = 123
    IEEE_Spider(JournalObj).run()