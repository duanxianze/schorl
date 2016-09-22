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

from src.Journals_Task.ElsevierSpider import *
from src.Journals_Task.SpringSpider import *
from src.Journals_Task.IEEE_Spider import *


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
