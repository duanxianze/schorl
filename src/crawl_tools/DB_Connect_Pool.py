#coding:utf-8
"""
@file:      DB_Connect_Pool
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-25 1:04
@description:
            数据库连接池
"""
import psycopg2,random,time
from multiprocessing.dummy import Pool as ThreadPool

class DB_Connect_Pool:
    def __init__(
        self,dbname,user,password,host=None,port=None,size=20
    ):
        self.size = size
        self.pool = []
        self.host = host
        self.port = port
        self.db_name = dbname
        self.user = user
        self.password = password
        self.init_pool()

    def new_coon(self):
        while(1):
            try:
                conn = psycopg2.connect(
                    host = self.host,
                    port = self.port,
                    dbname = self.db_name,
                    user = self.user,
                    password = self.password
                )
                conn.autocommit = True
                break
            except Exception as e:
                print(str(e))
                print('Launch DB Connect Error.Again...')
                time.sleep(2)
        return conn

    def add_new_coon_to_pool(self,index):
        self.pool.append(self.new_coon())
        print('Index {} lanuched ok!'.format(index))

    def init_pool(self):
        print('DB_POOL: Generating {} database connections...'\
              .format(self.size))
        if self.size > 8:
            thread_cot = 8
        else:
            thread_cot = self.size
        thread_pool = ThreadPool(thread_cot)
        thread_pool.map(self.add_new_coon_to_pool,range(self.size))
        thread_pool.terminate()
        print('DB_POOL: Created All Connects OK')

    def get_random_conn(self):
        return random.choice(self.pool)

    def new_db_cursor(self):
        return self.get_random_conn().cursor()