from crawl_tools.DB_Connect_Pool import DB_Connect_Pool
from crawl_tools.JsonConfig import DB_Config

configs = DB_Config('../db_config.json').to_dict()
for key in configs.keys():
    print(key,":",configs[key])

if configs['master_db_in']:
    REMOTE_HOST = None
    REMOTE_PORT = None
else:
    REMOTE_HOST = configs['host']
    REMOTE_PORT = configs['port']


DB_CONNS_POOL = DB_Connect_Pool(
    size = configs['local_pool_size'],
    dbname = configs['db_name'],
    user = configs['user'],
    password = configs['password'],
    #近期不做主从分离，都用远程库
    host = REMOTE_HOST,
    port = REMOTE_PORT
)

REMOTE_CONNS_POOL = DB_Connect_Pool(
    size = configs['remote_pool_size'],
    dbname = configs['db_name'],
    user = configs['user'],
    password = configs['password'],
    host = REMOTE_HOST,
    port = REMOTE_PORT
)
