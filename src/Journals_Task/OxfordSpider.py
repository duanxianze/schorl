#coding:utf-8
"""
@file:      OxfordSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-13 20:21
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

from journal_parser.Oxford_Parser import OxfordAllItemsPageParser,OxfordArticle
from Journals_Task.JournalSpider import JournalSpider
from crawl_tools.request_with_proxy import request_with_random_ua

class OxfordSpider(JournalSpider):
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.JournalObj = JournalObj
        self.url = JournalObj.site_source
        self.handle_spring_url()
        self.generate_volume_links()