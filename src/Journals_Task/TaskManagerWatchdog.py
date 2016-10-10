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

from crawl_tools.JsonConfig import DB_Config
from crawl_tools.WatchDog import WatchDog
import time,psycopg2

configs = DB_Config('../db_config.json').to_dict()

conn = psycopg2.connect(
    dbname = configs['db_name'],
    user = configs['user'],
    password = configs['password'],
    host = configs['host'],
    port = configs['port']
)
conn.autocommit = True
cur = conn.cursor()

class JournalTaskManagerWatchdog(WatchDog):
    def __init__(self,cmd_line,task_proc_cmd_line,pid=None):
        WatchDog.__init__(self,cmd_line,task_proc_cmd_line,pid)
        self.cur = cur
    
    @property
    def articles_amount(self):
        self.cur.execute(
            'select count(*) from articles'
        )
        return int(self.cur.fetchall()[0][0])

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
            'select count(*) from articles \
                  where category_id is not null'
        )
        return int(cur.fetchall()[0][0])

    def run(self):
        initial = True
        prev_amount = 0
        tf = open('../amount_log.txt','a+')
        while(1):
            try:
                for i in range(6):
                    amount = self.articles_amount
                    local_time = time.strftime(
                        "%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                    delta = amount - prev_amount
                    if initial:
                        delta = 0
                        initial = False
                    tf.write(str(amount)+','+local_time+','+str(delta)+'\n')
                    tf.close()
                    tf = open('../amount_log.txt','a+')
                    prev_amount = amount
                    self.print_log(tf)
                self.restart_task_proc()
            except Exception as e:
                print(str(e))
                self.cur = conn.cursor()

    def print_log(self,tf):
        for i in range(1,60):
            local_t = time.strftime(
                "%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            if self.task_proc_status in ['dead','zombie']:
                tf.write('restart,'+local_t+'\n')
                print('task ok or network error')
                self.restart_network('tonylu716')
                self.restart_task_proc()
            time.sleep(10)
        try:
            print('WatchDog:\n\t{},\t{},\t{},\t{},\t{},\t{},\t{}'\
                .format(
                    self.articles_amount,
                    self.task_proc_status,
                    self.AC_amount,
                    self.SC_amount,
                    self.SchArea_amount,
                    self.SchArticle_amount,
                    local_t
                )
            )
        except Exception as e:
            print(str(e))
            self.cur = conn.cursor()


if __name__=="__main__":
    import platform
    if os.name=='nt':
        if platform.processor()=='Intel64 Family 6 Model 69 Stepping 1, GenuineIntel':
            self_cmd_line=['C:\\Python33\\python.exe','Q:/scholar_articles/src/Journals_Task/TaskManagerWatchdog.py']
            proc_cmd_line=['C:\\Python33\\python.exe','Q:/scholar_articles/src/Journals_Task/run.py']
        elif platform.processor()=='Intel64 Family 6 Model 58 Stepping 9, GenuineIntel':
            self_cmd_line=['D:\\Python33\\python.exe','E:/scholar_articles/src/Journals_Task/TaskManagerWatchdog.py']
            proc_cmd_line=['D:\\Python33\\python.exe','E:/scholar_articles/src/Journals_Task/run.py']
        else:
            pass
    else:
        self_cmd_line = ['python3', 'TaskManagerWatchdog.py']
        proc_cmd_line = ['python3','run.py']
    JournalTaskManagerWatchdog(self_cmd_line,proc_cmd_line).run()
