#coding:utf-8
"""
@file:      TaylorFrancisSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-01 3:52
@description:
            --
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)


from journal_parser.TaylorFrancis_Parser import TaylorFrancisArticle,TaylorFrancisParser
from Journals_Task.JournalSpider import JournalSpider
from crawl_tools.request_with_proxy import request_with_random_ua

class TaylorFrancisSpider(JournalSpider):
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.JournalObj = JournalObj
        self.url = JournalObj.site_source
        self.handle_spring_url()
        self.generate_volume_links()

    def handle_taylor_url(self):
        pass

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            return
        pass

    def run(self):
        self._run(
            AllItemsPageParser = TaylorFrancisParser,
            JournalArticle = TaylorFrancisArticle
        )