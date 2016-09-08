#coding:utf-8
"""
@file:      Elsevier_generator_watchdog.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-06 13:56
@description:
            监控获取Elsevier生成pdf_url的任务
"""
from crawl_tools.WatchDog import WatchDog
from journal_pdf_url_generators.Elsevier_pdf_url_generator import *
import time

class Elsevier_Generator_Watchdog(WatchDog):
    def __init__(self,self_cmd_line,proc_cmd_line,pid=None):
        WatchDog.__init__(self,self_cmd_line,proc_cmd_line,pid)

    @property
    def counts_of_unfinished_items(self):
        cur.execute(
            "select count(*) from articles where journal_temp_info like '%Elsevier%' and resource_link is null"
        )
        return cur.fetchall()[0][0]

    @property
    def counts_of_finished_items(self):
        cur.execute(
            "select count(*) from articles where journal_temp_info like '%Elsevier%' and resource_link is not null"
        )
        return cur.fetchall()[0][0]

    def run(self):
        prev = 0
        delta_zero_cot = 0
        while(1):
            try:
                current = self.counts_of_finished_items
                delta = current - prev
                prev = current
                if delta_zero_cot > 5 or self.task_proc_status == 'dead':
                    self.restart_task_proc()
                    delta_zero_cot = 0
                if delta==0:
                    delta_zero_cot += 1
                else:
                    delta_zero_cot = 0
                print('WatchDog:\n\t{},\t{},\t{},\t{},\t{},\t{}'.format(
                        self.counts_of_finished_items,
                        self.counts_of_unfinished_items,
                        delta,
                        delta_zero_cot,
                        self.task_proc_status,
                        time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                    )
                )
            except:
                pass
            time.sleep(10)


if __name__=="__main__":
    import os,platform
    if os.name=='nt':
        if platform.processor()=='Intel64 Family 6 Model 69 Stepping 1, GenuineIntel':
            self_cmd_line=['D:\\python2.7\\python.exe','Q:/scholar_articles/src/journal_pdf_url_generators/Elsevier_generator_watchdog.py']
            proc_cmd_line=['D:\\python2.7\\python.exe','Q:/scholar_articles/src/journal_pdf_url_generators/Elsevier_pdf_url_generator.py']
        elif platform.processor()=='Intel64 Family 6 Model 58 Stepping 9, GenuineIntel':
            self_cmd_line=['C:\\Python27\\python.exe','F:/scholar_articles/src/journal_pdf_url_generators/Elsevier_generator_watchdog.py']
            proc_cmd_line=['C:\\Python27\\python.exe','F:/scholar_articles/src/journal_pdf_url_generators/Elsevier_pdf_url_generator.py']
        else:
            pass
    else:
        self_cmd_line=['python','Elsevier_generator_watchdog.py']
        proc_cmd_line=['python','Elsevier_pdf_url_generator.py']
    Elsevier_Generator_Watchdog(self_cmd_line,proc_cmd_line).run()
