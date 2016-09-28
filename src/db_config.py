from crawl_tools.DB_Connect_Pool import DB_Connect_Pool
import os

#windows机器为主数据库

if os.name=='nt':
    REMOTE_HOST = '192.168.2.100'
    REMOTE_PORT = 5432
else:
    REMOTE_HOST = '192.168.2.100'
    REMOTE_PORT = 5432


DB_CONNS_POOL = DB_Connect_Pool(
    size = 3,
    dbname = "sf_development",
    user = "lyn",
    password = "tonylu716",
    host = REMOTE_HOST,
    port = REMOTE_PORT
)

REMOTE_CONNS_POOL = DB_Connect_Pool(
    size = 4,
    dbname = "sf_development",
    user = "lyn",
    password = "tonylu716",
    host = REMOTE_HOST,
    port = REMOTE_PORT
)

if __name__=="__main__":
    print(DB_CONNS_POOL.get_random_conn(),REMOTE_CONNS_POOL.get_random_conn())