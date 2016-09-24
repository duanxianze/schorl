from crawl_tools.DB_Connect_Pool import DB_Connect_Pool
import os

if os.name=='nt':
    HOST = '45.32.11.113'
    PORT = 5432
else:
    HOST = None
    PORT = None


DB_CONNS_POOL = DB_Connect_Pool(
    size=20,
    dbname = "sf_development",
    user = "lyn",
    password = "tonylu716",
    host = HOST,
    port = PORT
)


if __name__=="__main__":
    print(DB_CONNS_POOL.new_db_cursor())
    print(DB_CONNS_POOL.new_coon())