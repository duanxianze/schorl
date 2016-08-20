#coding:utf-8
"""
@file:      pdf_download_watchdog.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    2.7
@editor:    PyCharm
@create:    2016-08-19 13:36
@description:
            关于pdf下载的数据监视器类，继承于基本的看门狗类
"""

from WatchDog import WatchDog
from download import *
import time,os


class Pdf_Download_Watchdog(WatchDog):
    def __init__(self,proc_cmd_line,pid=None):
        WatchDog.__init__(self,proc_cmd_line,pid)

    @property
    def counts_of_finished_db_item(self,extend_cursor=None):
        #db显示已下载项的数量
        if extend_cursor:
            cursor = extend_cursor
        else:
            cursor = cur
        cursor.execute(
            "select count(id) from articles where is_downloaded = 1"
        )
        return int(cur.fetchall()[0][0])

    @property
    def counts_of_unfinished_db_item(self,extend_cursor=None):
        #db显示未下载项的数量
        if extend_cursor:
            cursor = extend_cursor
        else:
            cursor = cur
        cursor.execute(
            "select count(*) from articles where is_downloaded = 0"
        )
        return int(cursor.fetchall()[0][0])

    @property
    def counts_of_pdf_files(self,extend_folder=None):
        #下载文件夹中pdf文件的数量
        if extend_folder:
            folder = extend_folder
        else:
            folder = DOWNLOAD_FOLDER
        return len(os.listdir(folder))

    def run(self):
        delta = 0
        prev_cot = 0
        delta_zero_cot = 0
        while(1):
            print('Dog:\n\t{},\t{},\t{},\t{},\t{}'.format(
                    self.counts_of_unfinished_db_item,
                    self.counts_of_pdf_files,
                    delta,
                    delta_zero_cot,
                    time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                )
            )
            current_cot = self.counts_of_unfinished_db_item
            delta = prev_cot - current_cot
            prev_cot = current_cot
            if delta==0:
                delta_zero_cot += 1
            else:
                delta_zero_cot = 0
            if delta_zero_cot==6:
                self.restart()
            time.sleep(10)


if __name__=='__main__':
    pdf_watchdog = Pdf_Download_Watchdog(
        proc_cmd_line = ['C:\\Python27\\python.exe', 'F:/scholar_articles/src/download.py']
    )
    pdf_watchdog.run()
