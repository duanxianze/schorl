from bs4 import BeautifulSoup
from random import randint
from request_with_proxy import request_with_proxy
import psycopg2
import time
from fake_useragent import UserAgent

ua = UserAgent()

random_port = lambda x, y: randint(x, y)

conn = psycopg2.connect(dbname="sf_development", user="gao", password="gaotongfei13")
conn.autocommit = True
cur = conn.cursor()

while True:
    #cur.execute("select id, google_id from articles where id > 314060 and bibtex is null")
    cur.execute("select id, google_id from articles where id > 314040 and bibtex is null")
    result_sets = cur.fetchall()
    print("{} tasks running".format(len(result_sets)))
    for id, google_id in result_sets:
        bibtex = None
        time.sleep(1)
        rand_port = random_port(9054, 9155)
        print(rand_port)
        proxies = {
                'http': 'socks5://127.0.0.1:{0}'.format(rand_port),
                'https': 'socks5://127.0.0.1:{0}'.format(rand_port)
        }

        url = 'https://scholar.google.com/scholar?q=info:{}:scholar.google.com/&output=cite&scirp=0&hl=en'.format(google_id)
        headers = {'User-Agent': ua.random}
        print(requests.get('https://api.ipify.org', proxies=proxies, headers=headers).content)
        response = requests.get(url, proxies=proxies, timeout=20, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            url = soup.select("#gs_citi > a")[0]['href']
            full_url = "https://scholar.google.com" + url
            bibtex_response = requests.get(full_url, proxies=proxies, timeout=20, headers=headers)
            if bibtex_response:
                bibtex = bibtex_response.text

        cur.execute("update articles set bibtex = %s where id = %s", (bibtex, id))
