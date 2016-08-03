#coding:utf-8
'''
amount_status.py：
    用于统计数据库articles表数据量，了解爬取速率
'''

import psycopg2,time,csv
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


def update_csv():
    fr = open('amount_log.txt','r')
    cf = open('amount_log.csv','wb')
    cw = csv.writer(cf)
    line = 'hello'
    while line:
        line = fr.readline()[:-1]
        line_data = line.split(',')
        print(line_data)
        if len(line_data)==1:
            break
        '''
        for data in line_data:
            data = data.encode('utf-8')
        '''
        num = line_data[0]
        time = line_data[1]
        delta = line_data[2]
        print([num,time,delta])
        cw.writerow([num,time,delta])
    cf.close()


if __name__=='__main__':
    tf = open('amount_log.txt','a+')
    prev_amount = 0
    initial = True
    while(1):
        amount = articles_amount(cur)
        local_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        delta = amount - prev_amount
        if initial:
            delta = 0
            initial = False
        tf.write(str(amount)+','+local_time+','+str(delta)+'\n')
        tf.close()
        #update_csv()# operation not in server
        tf = open('amount_log.txt','a+')
        prev_amount = amount
        time.sleep(10*60)#每十分钟统计一次
