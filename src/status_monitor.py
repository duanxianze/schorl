#coding:utf-8
"""
@file:      artciles_watchdog.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-8-12 14:30
@description:
            用于统计数据库articles表数据量,记录在log里,了解爬取速率,
            若delta数据长时为零，则邮件通知管理员
"""

import psycopg2,time,csv
from emailClass import Email

COUNT_FROM_ARTICLES = 'select count(*) from articles'
DB_NAME = "sf_development"
USER = "gao"
PASSWORD = "123123"
conn = psycopg2.connect(
    "dbname={0} user={1} password={2}".format(DB_NAME, USER, PASSWORD)
)
conn.autocommit = True
cur = conn.cursor()


def articles_amount(cur):
    cur.execute(
        'select count(*) from articles'
    )
    return cur.fetchall()[0][0]

import os
def send_mail():
    #py33 以上smtp.starttls()会报错，移到其他脚本上用py27执行
    os.system(
        '/usr/bin/python2.7 ~/scholar_articles/src/emailClass.py'
    )


if __name__=='__main__':
    #send_mail()
    tf = open('amount_log.txt','a+')
    prev_amount = 0
    initial = True
    delta_zero_cot = 0
    while(1):
        amount = articles_amount(cur)
        local_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        delta = amount - prev_amount
        if delta==0:
            delta_zero_cot += 1
        else:
            delta_zero_cot = 0
        if delta_zero_cot==6:
            send_mail()
            delta_zero_cot = 0
        if initial:
            delta = 0
            initial = False
        tf.write(str(amount)+','+local_time+','+str(delta)+'\n')
        tf.close()
        #update_csv()# operation not in server
        tf = open('amount_log.txt','a+')
        prev_amount = amount
        time.sleep(10*60)#每十分钟统计一次
