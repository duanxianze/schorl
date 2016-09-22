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
        JournalSpider.__init__(self,JournalObj)
        self.JournalObj = JournalObj
        self.url = JournalObj.site_source
        self.handle_spring_url()
        self.generate_volume_links()

    def handle_spring_url(self):
        if 'www.springer.com' in self.url:
            self.spring_journal_id = self.url.split('/')[-1]
            self.url = 'http://link.springer.com/search?sortOrder=newestFirst&showAll=true&facet-content-type=Article&facet-journal-id='+self.spring_journal_id
        print(self.url)

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            return
        #假如数据库中已保存，直接读取即可，无需生成
        for page_num in range(1,SpringParser(
            html_source=request_with_random_ua(self.url).text
        ).pages_amount+1):
            page_url = 'http://link.springer.com/search/page/{}?facet-journal-id={}&showAll=true&facet-content-type=Article&sortOrder=newestFirst'\
                            .format(page_num,self.spring_journal_id)
            self.volume_links.append(page_url)

    def run(self):
        unfinished_links = self.get_unfinished_volume_links()
        for volume_link in unfinished_links:
            secs = SpringParser(
                html_source=request_with_random_ua(volume_link).text
            ).secs
            for sec in secs:
                while(1):
                    try:
                        SpringArticle(sec,self.JournalObj).save_to_db()
                        break
                    except psycopg2.OperationalError:
                        print('db error,again')
                        time.sleep(2)
            print('xxxxxxxxxxxxxxxxxx')
            if len(secs)>0:
                self.mark_volume_ok(volume_link)
        if len(unfinished_links)>0:
            self.mark_journal_ok()


if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    JournalObj=Journal()
    JournalObj.site_source = 'http://www.springer.com/computer+science/image+processing/journal/10055'
    SpringSpider(
        JournalObj
    ).run()