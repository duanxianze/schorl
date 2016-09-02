#coding:utf-8
"""
@file:      IEEE_generator_watchdog
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    2.7
@editor:    PyCharm
@create:    2016-09-02 20:39
@description:
            监控获取IEEE pdf_url的任务
"""
from WatchDog import WatchDog
from IEEE_pdf_url_generator import *
import time

class IEEE_Generator_Watchdog(WatchDog):
    def __init__(self,self_cmd_line,proc_cmd_line,pid=None):
        WatchDog.__init__(self,self_cmd_line,proc_cmd_line,pid)

    @property
    def counts_of_unfinished_items(self):
        cur.execute(
            "select count(*) from articles where journal_temp_info like '%ieee%' and resource_link is null and id > 314060"
        )
        return cur.fetchall()[0][0]

    @property
    def counts_of_finished_items(self):
        cur.execute(
            "select count(*) from articles where journal_temp_info like '%ieee%' and resource_link is not null and id > 314060"
        )
        return cur.fetchall()[0][0]

    def run(self):
        while(1):
            if self.task_proc_status is 'dead':
                self.restart_task_proc()
            print('WatchDog:\n\t{},\t{},\t{},\t{}'.format(
                    self.counts_of_finished_items,
                    self.counts_of_unfinished_items,
                    self.task_proc_status,
                    time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                )
            )


if __name__=="__main__":
    IEEE_Generator_Watchdog(
        self_cmd_line=['C:\\Python27\\python.exe','F:/scholar_articles/src/IEEE_generator_watchdog.py'],
        proc_cmd_line=['C:\\Python27\\python.exe','F:/scholar_articles/src/IEEE_pdf_url_generator.py']
    ).run()
