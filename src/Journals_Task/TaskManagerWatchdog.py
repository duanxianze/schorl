#coding:utf-8
"""
@file:      TaskManagerWatchdog
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-23 16:09
@description:
            监控主爬虫的运行情况，包括记录数据，异常自启等
"""
import sys,os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from GoogleScholar_Task.articles_watchdog import Artciles_Spider_WatchDog
from db_config import new_db_cursor
import time

class JournalTaskManagerWatchdog(Artciles_Spider_WatchDog):
    def __init__(self,cmd_line,task_proc_cmd_line,pid=None):
        Artciles_Spider_WatchDog.__init__(self,cmd_line,task_proc_cmd_line,pid)
        self.cur = new_db_cursor()

    @property
    def volumes_amount(self):
        cur = self.cur
        cur.execute(
            'select count(*) from journal_volume'
        )
        return int(cur.fetchall()[0][0])

    @property
    def SC_amount(self):
        cur = self.cur
        cur.execute(
            'select count(*) from temp_scholar_category'
        )
        return int(cur.fetchall()[0][0])

    @property
    def SchArea_amount(self):
        cur = self.cur
        cur.execute(
            'select count(*) from temp_scholar_area'
        )
        return int(cur.fetchall()[0][0])

    @property
    def SchArticle_amount(self):
        cur = self.cur
        cur.execute(
            'select count(*) from temp_scholar_article'
        )
        return int(cur.fetchall()[0][0])

    @property
    def AC_amount(self):
        cur = self.cur
        cur.execute(
            'select count(*) from articles where category_id is not null'
        )
        return int(cur.fetchall()[0][0])

    def run(self):
        initial = True
        tf = open('../amount_log.txt','a+')
        while(1):
            amount = self.articles_amount
            local_time = time.strftime(
                "%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            if initial:
                delta = 0
                initial = False
            if self.task_proc_status=='dead':
                self.restart_task_proc()
            tf.write(str(amount)+','+local_time+','+str(delta)+'\n')
            tf.close()
            tf = open('../amount_log.txt','a+')
            self.print_log()


    def print_log(self):
        for i in range(1,60):
            print('WatchDog:\n\t{},\t{},\t{},\t{},\t{},\t{},\t{}'.format(
                self.articles_amount,
                self.task_proc_status,
                self.AC_amount,
                self.SC_amount,
                self.SchArea_amount,
                self.SchArticle_amount,
                time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                )
            )
            time.sleep(10)


if __name__=="__main__":
    if os.name is 'nt':
        proc_cmd_line = ['D:\\Python33\\python.exe','E:/scholar_articles/src/Journals_Task/MajorTaskManager.py']
        self_cmd_line = ['D:\\Python33\\python.exe','E:/scholar_articles/src/Journals_Task/TaskManagerWatchdog.py']
    else:
        #os.system('source ~/scholar_articles/py3env/bin/activate')
        proc_cmd_line = ['python3', 'ArticlesSpider.py']
        self_cmd_line = ['python3','articles_watchdog.py']

    JournalTaskManagerWatchdog(self_cmd_line,proc_cmd_line).run()