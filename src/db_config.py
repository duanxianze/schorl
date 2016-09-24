import os,psycopg2,time,random
from multiprocessing.dummy import Pool as ThreadPool

class DB_Pool:
    def __init__(self,size=20,
            dbname = "sf_development",
            user = "lyn",
            password = "tonylu716",
            host = '45.32.11.113',
            port = 5432,
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
        if os.name is 'nt':
            conn = psycopg2.connect(
                host = self.host,
                port = self.port,
                dbname = self.db_name,
                user = self.user,
                password = self.password
            )
        else:
            conn = psycopg2.connect(
                dbname = self.db_name,
                user = self.user,
                password = self.password
            )
        conn.autocommit = True
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
        print('DB_POOL: Created ok')

    def get_random_conn(self):
        return random.choice(self.pool)

    def new_db_cursor(self):
        return self.get_random_conn().cursor()



DB_CONNS_POOL = DB_Pool(size=10)
