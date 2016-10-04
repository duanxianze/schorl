#coding:utf-8
"""
@file:      artciles_watchdog.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-8-20 18:30
@description:
            用于统计数据库articles表数据量,记录在log里,了解爬取速率,
            若delta数据长时为零，则邮件通知管理员
"""

import sys,os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from crawl_tools.WatchDog import WatchDog
import psycopg2,time

REMOTE_HOST = '45.76.71.26'
REMOTE_PORT = 5432

conn = psycopg2.connect(
    dbname = "sf_development",
    user = "lyn",
    password = "tonylu716",
    host = REMOTE_HOST,
    port = REMOTE_PORT
)
conn.autocommit = True
cur = conn.cursor()

class Artciles_Spider_WatchDog(WatchDog):
    def __init__(self,cmd_line,task_proc_cmd_line,pid=None):
        WatchDog.__init__(self,cmd_line,task_proc_cmd_line,pid)

    @property
    def articles_amount(self):
        cur.execute(
            'select count(*) from articles'
        )
        return int(cur.fetchall()[0][0])

    def send_mail(self):
        #py33 以上smtp.starttls()会报错，移到其他脚本上用py27执行
        os.system(
            '/usr/bin/python2.7 ~/scholar_articles/src/emailClass.py'
        )

    def _run(self):
        prev_amount = 0
        initial = True
        delta_zero_cot = 0
        tf = open('amount_log.txt','a+')
        while(1):
            amount = self.articles_amount
            local_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            delta = amount - prev_amount
            if delta==0:
                delta_zero_cot += 1
            else:
                delta_zero_cot = 0
            if delta_zero_cot>=6:
                #self.restart_task_proc()
                self.send_mail()
                delta_zero_cot = 0
            if delta_zero_cot>=3:
                self.restart_task_proc()
                tf.write('restart,'+local_time+'\n')
            if initial:
                delta = 0
                initial = False
            tf.write(str(amount)+','+local_time+','+str(delta)+'\n')
            tf.close()
            #update_csv()# operation not in server
            tf = open('amount_log.txt','a+')
            prev_amount = amount
            self.print_log()


    def print_log(self):
        for i in range(1,60):
            print('WatchDog:\n\t{},\t{},\t{}'.format(
                    self.articles_amount,
                    self.task_proc_status,
                    time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                )
            )
            time.sleep(10)


if __name__=='__main__':
    if os.name is 'nt':
        proc_cmd_line = ['C:\\Python27\\python.exe','F:/scholar_articles/src/GoogleTask/ArticlesSpider.py']
        self_cmd_line = ['C:\\Python27\\python.exe','F:/scholar_articles/src/GoogleTask/articles_watchdog.py']
    else:
        #os.system('source ~/scholar_articles/py3env/bin/activate')
        proc_cmd_line = ['python3', 'ArticlesSpider.py']
        self_cmd_line = ['python3','articles_watchdog.py']

    Artciles_Spider_WatchDog(self_cmd_line,proc_cmd_line)._run()


