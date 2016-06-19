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
        url = 'https://scholar.google.com/scholar?q=info:{}:scholar.google.com/&output=cite&scirp=0&hl=en'.format(google_id)
        #print(request_with_proxy('https://api.ipify.org', use_ss=False).content)
        response = request_with_proxy(url, timeout=20, use_ss=False, sleep=1)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            citi = soup.select("#gs_citi > a")
            if citi:
                url = citi[0]['href'] 
                full_url = "https://scholar.google.com" + url
                bibtex_response = request_with_proxy(full_url, timeout=20, use_ss=False, sleep=1)
                if bibtex_response:
                    bibtex = bibtex_response.text
                    print(bibtex)
                else:
                    print('no bibtex scraped')

        else:
            print(response.status_code)
        cur.execute("update articles set bibtex = %s where id = %s", (bibtex, id))

    time.sleep(3600)
