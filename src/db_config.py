from crawl_tools.DB_Connect_Pool import DB_Connect_Pool
import os

#windows机器为主数据库

if os.name=='nt':
    REMOTE_HOST = None
    REMOTE_PORT = None
else:
    REMOTE_HOST = None
    REMOTE_PORT = None


DB_CONNS_POOL = DB_Connect_Pool(
    size = 32,
    dbname = "sf_development",
    user = "lyn",
    password = "tonylu716",
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