import requests
from random import randint
import psycopg2
import time

random_port = lambda x, y: randint(x, y)

conn = psycopg2.connect(dbname="sf_development", user="gao", password="gaotongfei13")
cur = conn.cursor()

while True:
    time.sleep(1)
    rand_port = random_port(9054, 9093)
    print(rand_port)
    proxies = {
            'http': 'socks5://127.0.0.1:{0}'.format(rand_port),
            'https': 'socks5://127.0.0.1:{0}'.format(rand_port)
    }
    cur.execute("select id, google_id from articles where id >= 314060")
    cur.fetchall()
    #print(requests.get('https://api.ipify.org/', proxies=proxies).content)
