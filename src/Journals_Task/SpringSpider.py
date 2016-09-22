#coding:utf-8
"""
@file:      SpringSpider.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-17 19:56
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

from journal_parser.Spring_Parser import SpringArticle,SpringParser
from Journals_Task.JournalSpider import JournalSpider
from crawl_tools.request_with_proxy import request_with_random_ua
import psycopg2,time

class SpringSpider(JournalSpider):
    '''
        sample_url: http://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=778
    '''
    def __init__(self,JournalObj):
        self.JournalObj = JournalObj
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.handle_spring_url()

    def handle_spring_url(self):
        if 'www.springer.com' in self.url:
            self.spring_journal_id = self.url.split('/')[-1]
            self.url = 'http://link.springer.com/search?sortOrder=newestFirst&showAll=false&facet-content-type=Article&facet-journal-id='+self.spring_journal_id

    def run(self):
        parser = SpringParser(
            html_source=request_with_random_ua(self.url).text
        )
        for page_num in range(1,parser.pages_amount+1):
            page_url = 'http://link.springer.com/search/page/{}?facet-journal-id={}&showAll=false&facet-content-type=Article&sortOrder=newestFirst'\
                            .format(page_num,self.spring_journal_id)
            for sec in SpringParser(
                html_source=request_with_random_ua(page_url).text
            ).secs:
                while(1):
                    try:
                        SpringArticle(sec,self.JournalObj).save_to_db()
                    except psycopg2.OperationalError:
                        print('db error,again')
                        time.sleep(2)
        self.mark_journal_ok()


if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    JournalObj=Journal()
    JournalObj.site_source = 'http://www.springer.com/computer+science/image+processing/journal/10055'
    SpringSpider(
        JournalObj
    ).run()