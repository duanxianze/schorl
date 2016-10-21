import sys,os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from crawl_tools.JsonConfig import DB_Config
import psycopg2

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

def journal_is_crawled(journal_id):
    sql = "select count(*) from journal_volume \
        where journal_sjr_id = {} and is_crawled =false".format(journal_id)
    cur.execute(sql)
    cot = cur.fetchall()[0][0]
    sql = "select count(*) from journal_volume \
        where journal_sjr_id = {}".format(journal_id)
    cur.execute(sql)
    cot2 = cur.fetchall()[0][0]
    print(cot,cot2,journal_id)
    if cot > 0:
         return False
    else:
         return True

def update(journal_id):
    sql = 'update journal set is_crawled_all_article=false \
                 where sjr_id={}'.format(journal_id)
    cur.execute(sql)
    print('{} update ok'.format(journal_id))


sql = "select sjr_id from journal where is_crawled_all_article \
                and site_source like '%informa%'"

cur.execute(sql)
data = cur.fetchall()
print (len(data))

import time
time.sleep(2)

for journal_id in data:
    if not journal_is_crawled(journal_id[0]):
        update(journal_id[0])
    print('------')

