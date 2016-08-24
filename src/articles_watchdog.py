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

import time,os
from WatchDog import WatchDog
from ArticlesSpider import *


class Artciles_Spider_WatchDog(WatchDog):
    def __init__(self,self_cmd_line,proc_cmd_line,pid=None):
        WatchDog.__init__(self,self_cmd_line,proc_cmd_line,pid)

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

    def run(self):
        prev_amount = 0
        initial = True
        delta_zero_cot = 0
        tf = open('amount_log.txt','a+')
        while(1):
            amount = self.articles_amount
            local_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            delta = amount - prev_amount
            current_status = self.proc.status()
            if delta==0:
                delta_zero_cot += 1
            else:
                delta_zero_cot = 0
            if delta_zero_cot>=6:
                self.restart()
                #self.send_mail()
                delta_zero_cot = 0
            if initial:
                delta = 0
                initial = False
            tf.write(str(amount)+','+local_time+','+str(delta)+'\n')
            tf.close()
            #update_csv()# operation not in server
            tf = open('amount_log.txt','a+')
            prev_amount = amount
            for i in range(1,60):
                print('WatchDog:\n\t{},\t{},\t{},\t{},\t{}'.format(
                        amount,
                        delta,
                        delta_zero_cot,
                        current_status,
                        time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                    )
                )
                time.sleep(10)
            #time.sleep(60)#每十分钟统计一次


if __name__=='__main__':
    if os.name is 'nt':
        proc_cmd_line = ['C:\\Python27\\python.exe','F:/scholar_articles/src/ArticlesSpider.py']
    else:
        proc_cmd_line = ['python', 'ArticlesSpider.py']

    self_cmd_line = ['python','articles_watchdog.py']

    Artciles_Spider_WatchDog(self_cmd_line,proc_cmd_line).run()


