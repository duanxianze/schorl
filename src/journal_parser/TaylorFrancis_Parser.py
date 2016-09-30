#coding:utf-8
"""
@file:      TaylorFrancis_Parser
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-01 3:46
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

from bs4 import BeautifulSoup
from journal_parser.JournalArticle import JournalArticle

class TaylorFrancisParser:
    '''
        sample url:http://www.tandfonline.com/toc/fjps20/current
    '''
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('TaylorFrancis.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source,'lxml')

    @property
    def sections(self):
        pass

    @property
    def volume_links(self):
        pass


class TaylorFrancisArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id):
        self.sec = sec
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()