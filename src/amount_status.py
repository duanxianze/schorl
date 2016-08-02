#coding:utf-8
import psycopg2,time

def articles_amount(cur):
    cur.execute(
        'select count(*) from articles'
    )
    return cur.fetchall()[0][0]


if __name__=='__main__':
    '''设置数据库'''
    DB_NAME = "sf_development"
    USER = "gao"
    PASSWORD = "123123"
    '''连接数据库'''
    conn = psycopg2.connect(
        "dbname={0} user={1} password={2}".format(DB_NAME, USER, PASSWORD)
    )
    conn.autocommit = True  #设置数据库自动提交
    cur = conn.cursor()

    f = open('amount_log.txt','a')

    while(1):
        aa = articles_amount(cur)
        local_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        f.write(str(aa)+'  '+local_time+'\n')
        f.close()
        f = open('amount_log.txt','a')
        time.sleep(60*10)#每十分钟统计一次
