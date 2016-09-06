#coding:utf-8
"""
@file:      pdf_download_watchdog.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    2.7
@editor:    PyCharm
@create:    2016-08-20 13:36
@description:
            关于pdf下载的数据监视器类，继承于基本的看门狗类
"""

from WatchDog import WatchDog
from download import *
import time,os


class Pdf_Download_Watchdog(WatchDog):
    def __init__(self,self_cmd_line,proc_cmd_line,pid=None):
        WatchDog.__init__(self,self_cmd_line,proc_cmd_line,pid,kill_prev=True)

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
            "select count(*) from articles where is_downloaded = 0 and resource_link is not null"
        )
        return int(cursor.fetchall()[0][0])

    @property
    def counts_of_exception_db_item(self,extend_cursor=None):
        #db显示未下载项的数量
        if extend_cursor:
            cursor = extend_cursor
        else:
            cursor = cur
        cursor.execute(
            "select count(*) from articles where is_downloaded = -1"
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
        prev_local_file_cot = 0
        delta_zero_cot = 0
        while(1):
            current_local_file_cot = self.counts_of_pdf_files
            delta = current_local_file_cot - prev_local_file_cot
            prev_local_file_cot = current_local_file_cot
            current_status = self.task_proc_status
            if delta==0:
                delta_zero_cot += 1
            else:
                delta_zero_cot = 0
            if delta_zero_cot>=3 or current_status is 'dead':
                self.restart_task_proc()
                delta_zero_cot = 0
            print('WatchDog:\n\t{},\t{},\t{},\t{},\t{},\t{},\n\t{}'.format(
                    self.counts_of_unfinished_db_item,
                    self.counts_of_exception_db_item,
                    current_local_file_cot,
                    delta,
                    delta_zero_cot,
                    current_status,
                    time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                )
            )
            time.sleep(10)


if __name__=='__main__':
    import os,platform
    if platform.processor()=='Intel64 Family 6 Model 69 Stepping 1, GenuineIntel':
        self_cmd_line=['D:\\python2.7\\python.exe','Q:/scholar_articles/src/pdf_download_watchdog.py']
        proc_cmd_line=['D:\\python2.7\\python.exe','Q:/scholar_articles/src/download.py']
    elif platform.processor()=='Intel64 Family 6 Model 58 Stepping 9, GenuineIntel':
        self_cmd_line=['C:\\Python27\\python.exe','F:/scholar_articles/src/pdf_download_watchdog.py']
        proc_cmd_line=['C:\\Python27\\python.exe','F:/scholar_articles/src/download.py']
    else:
        pass
    Pdf_Download_Watchdog(self_cmd_line,proc_cmd_line).run()
