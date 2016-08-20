#coding:utf-8
"""
@file:      test_connenct_distance_db.py.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-19 13:36
@description:
            --
"""

from WatchDog import *
import time

pdf_watchdog = WatchDog(
    proc_cmd_line = ['C:\\Python27\\python.exe', 'F:/scholar_articles/src/download.py']
)

while(1):

    pdf_watchdog.restart()
    time.sleep(5)