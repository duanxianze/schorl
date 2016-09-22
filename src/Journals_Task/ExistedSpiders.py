#coding:utf-8
"""
@file:      ExistedSpiders.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-18 0:51
@description:
            存放已经写好的publisher爬虫包指向以及配置
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)


from Journals_Task.ElsevierSpider import *
from Journals_Task.SpringSpider import *
from Journals_Task.IEEE_Spider import *


EXISTED_SPIDERS = [
    {
        'publisherSpiderClass': ElsevierSpider,
        'publisherKeywords':    ['elsevier','sciencedirect'],
        'need_webdriver':       True
    },{
        'publisherSpiderClass': SpringSpider,
        'publisherKeywords':    ['springer'],
        'need_webdriver':       False
    },{
        'publisherSpiderClass': IEEE_Spider,
        'publisherKeywords':    ['ieee'],
        'need_webdriver':       False
    }
]
