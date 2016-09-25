from crawl_tools.DB_Connect_Pool import DB_Connect_Pool
import os

#linux机器为主数据库

if os.name=='nt':
    REMOTE_HOST = '45.32.11.113'
    REMOTE_PORT = 5432
else:
    REMOTE_HOST = None
    REMOTE_PORT = None


DB_CONNS_POOL = DB_Connect_Pool(
    size=20,
    dbname = "sf_development",
    user = "lyn",
    password = "tonylu716",
)

REMOTE_CONNS_POOL = DB_Connect_Pool(
    size = 5,
    dbname = "sf_development",
    user = "lyn",
    password = "tonylu716",
    host = REMOTE_HOST,
    port = REMOTE_PORT
)

if __name__=="__main__":
    print(DB_CONNS_POOL.get_random_conn(),REMOTE_CONNS_POOL.get_random_conn())