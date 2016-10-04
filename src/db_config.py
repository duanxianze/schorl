from crawl_tools.DB_Connect_Pool import DB_Connect_Pool
import os,platform

IS_MASTER_DB = ( os.name!='nt' and platform.processor()=='x86_64' )

if IS_MASTER_DB:
    REMOTE_HOST = None
    REMOTE_PORT = None
else:
    REMOTE_HOST = '45.76.71.26'
    REMOTE_PORT = 5432

DB_CONNS_POOL = DB_Connect_Pool(
    size = 30,
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
