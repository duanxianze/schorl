#coding:utf-8
'''
    bibtex.py 用于获取每篇文章的bibtex信息
'''
from bs4 import BeautifulSoup
from random import randint
from request_with_proxy import request_with_proxy
import psycopg2
import time
from fake_useragent import UserAgent

ua = UserAgent()#实例化代理类

random_port = lambda x, y: randint(x, y)#随机分配端口

'''连接数据库'''
conn = psycopg2.connect(dbname="sf_development", user="gao", password="gaotongfei13")
conn.autocommit = True
cur = conn.cursor()

while True:
    '''查询数据库，得到bibtex为空的项目元组'''
    cur.execute("select id, google_id from articles where id > 314073 and bibtex is null")
    result_sets = cur.fetchall()
    print("{} tasks running".format(len(result_sets)))
    for id, google_id in result_sets:
        try:
            '''对于一篇文章（item）'''
            bibtex = None
            url = 'https://scholar.google.com/scholar?q=info:{}:scholar.google.com/&output=cite&scirp=0&hl=en'.format(google_id)

            print("id: {0} google_id: {1}".format(id, google_id))
            print("url: {}".format(url))
            #print(request_with_proxy('https://api.ipify.org', use_ss=False).content)
            '''爬虫访问文章url'''
            #response = request_with_proxy(url, timeout=20, use_ss=False, sleep=1)
            response = request_with_proxy(url, use_ss=True)
            if response.status_code == 200:
                print("response 200")
                '''若访问正常，对访问的返回结果注入BeautifulSoup模型'''
                soup = BeautifulSoup(response.text, "lxml")
                citi = soup.select("#gs_citi > a")
                with open(google_id+'.html', 'w') as f:
                    f.write(response.text)
                print(citi)
                if citi:
                    '''搜索节点，找到bibtex的url路径'''
                    url = citi[0]['href']
                    full_url = "https://scholar.google.com" + url
                    '''访问该路径，得到bibtex'''
                    bibtex_response = request_with_proxy(full_url)
                    print('bibtex url: {0}'.format(full_url))
                    print('bibtex site status code: {}'.format(bibtex_response.status_code))
                    if bibtex_response:
                        bibtex = bibtex_response.text
                        print(bibtex)
                    else:
                        print('no bibtex scraped')

            else:
                print(response.status_code)

            '''对于得到的每一个文章的bibtex，更新注入数据库'''
            cur.execute("update articles set bibtex = %s where id = %s", (bibtex, id))
        except Exception as e:
            print(e)

    '''爬取延时'''
    time.sleep(3600)
