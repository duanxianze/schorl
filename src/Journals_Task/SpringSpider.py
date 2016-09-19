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

from src.journal_parser.Spring_Parser import SpringArticle,SpringParser
from src.Journals_Task.JournalSpider import JournalSpider
from src.crawl_tools.request_with_proxy import request_with_random_ua

class SpringSpider(JournalSpider):
    '''
        sample_url: http://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=778
    '''
    def __init__(self,url,journal_id):
        JournalSpider.__init__(self,journal_id)
        self.url = url
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
                SpringArticle(sec,self.journal_id).show_in_cmd()


if __name__=="__main__":
    SpringSpider(
        url = 'http://www.springer.com/computer/database+management+%26+information+retrieval/journal/778',
        journal_id=23792
    ).run()