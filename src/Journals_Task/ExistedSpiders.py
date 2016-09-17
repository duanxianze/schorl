#coding:utf-8
"""
@file:      ExistedSpiders.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-18 0:51
@description:
            存放已经写好的publisher爬虫包
"""

from src.Journals_Task.ElsevierSpider import *
from src.Journals_Task.SpringSpider import *
from src.Journals_Task.IEEE_Spider import *


EXISTED_SPIDERS = [
    {'publisherSpiderClass':ElsevierSpider,  'publisherKeyword':'elseiver'},
    {'publisherSpiderClass':SpringSpider,    'publisherKeyword':'springer'},
    {'publisherSpiderClass':IEEE_Spider,     'publisherKeyword':'ieee'}
]
