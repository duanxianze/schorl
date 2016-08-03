#coding:utf-8
'''
amount_status.py：
    用于统计数据库articles表数据量，了解爬取速率
'''

import psycopg2,time,csv

def articles_amount(cur):
    cur.execute(
        'select count(*) from articles'
    )
    return cur.fetchall()[0][0]


DB_NAME = "sf_development"
USER = "gao"
PASSWORD = "gaotongfei13"
conn = psycopg2.connect(
    "dbname={0} user={1} password={2}".format(DB_NAME, USER, PASSWORD)
)
conn.autocommit = True
cur = conn.cursor()


if __name__=='__main__':
    csv_file = file('amount_log.csv','wb')
    cw = csv.writer(fileobj=csv_file)
    prev_amount = 0
    while(1):
        amount = articles_amount(cur)
        local_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        delta = amount - prev_amount
        cw.write([amount,local_time,delta])
        csv_file.close()
        csv_file = file('amount_log.csv','wb')
        cw = csv.writer(fileobj=csv_file)
        prev_amount = amount
        time.sleep(60*10)#每十分钟统计一次
