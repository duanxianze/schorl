#coding:utf-8
"""
@file:      IEEE_download.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-31 14:43
@description:
            专门为IEEE出版社的pdf下载模块
"""

import os,psycopg2,random
from multiprocessing.dummy import Pool as ThreadPool
from IEEE_Parser import IEEE_HTML_Parser,Article,get_pdf_link
from DriversPool import DriversPool
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


if os.name is 'nt':
    conn = psycopg2.connect(
        host = '45.32.131.53',
        port = 5432,
        dbname = "sf_development",
        user = "gao",
        password = "gaotongfei13"
    )
else:
    conn = psycopg2.connect(
        dbname = "sf_development",
        user = "gao",
        password = "gaotongfei13"
    )
cur = conn.cursor()
conn.autocommit = True

class IEEE_Search_Model:
    def __init__(self,title,google_id,driver):
        self.title = title
        self.google_id = google_id
        while(1):
            driver.get(
                url = 'http://ieeexplore.ieee.org/search/searchresult.jsp?queryText={}&newsearch=true'\
                    .format('%20'.join(title.split(' ')))
            )#尝试selenium进入搜索页
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'List-results-items'))
                )#等待网站的ajax加载完，items呈现在页面上，交给parser处理
                try:
                    title = title[:40]
                except:
                    pass
                print('IEEE_Search_Model:\n\tGot search result of <{}>\n\tDeliver to parser...'.format(title+'...'))
                break
            except Exception as e:
                print('IEEE_Search_Model:\n\tError in search page:{}, reload again...'.format(str(e)))
        self.sec = IEEE_HTML_Parser(driver).sections[0]
        self.driver = driver

    def get_pdf_url(self):
        pdf_page_url = Article(self.sec).pdf_page_url
        if pdf_page_url:
            try:
                cur.execute(
                    "update articles set pdf_temp_url = %s where google_id = %s",
                    (pdf_page_url,self.google_id)
                )
            except Exception as e:
                print('get_pdf_url()_update_pdf_temp_url:{}'.format(str(e)))
            return get_pdf_link(pdf_page_url,self.driver)


class IEEE_pdf_url_generator:
    def __init__(self):
        self.drivers_pool = []

    def get_unfinished_items(self,limit=10000):
        #从db中检索出出版社为IEEE的article title集
        cur.execute(
            "select title,google_id,pdf_temp_url from articles where resource_link is null and journal_temp_info like '%ieee%' limit {}".format(limit)
        )
        return cur.fetchall()

    def generate(self,unfinished_item):
        #从title出发，反馈pdf_url给db
        google_id = unfinished_item[1]
        pdf_temp_url = unfinished_item[2]
        print('IEEE_PDF_URL_Generator:\n\tGot task of {}'.format(google_id))
        #向pool索取一个空闲的driver对象
        driverObj = self.drivers_pool.get_one_free_driver(wait=True)
        driverObj.status = 'busy'
        if pdf_temp_url:
            pdf_url = get_pdf_link(pdf_temp_url,driverObj.engine)
        else:
            pdf_url = IEEE_Search_Model(
                title = unfinished_item[0],
                google_id = google_id,
                driver = driverObj.engine
            ).get_pdf_url()
        driverObj.status = 'free'
        if not pdf_url:
            print('IEEE_PDF_URL_Generator:\n\tFail to get pdf_url of {}'.format(google_id))
            return
        print('IEEE_Article_Parser:\n\tGot pdf_url:{}'.format(pdf_url))
        self.mark_db(pdf_url,google_id)

    def mark_db(self,pdf_url,google_id):
        try:
            cur.execute(
                "update articles set resource_link = %s,resource_type = 'PDF' where google_id = %s",
                (pdf_url,google_id)
            )
            print('Database:\n\tupdate pdf_url of {} ok '.format(google_id))
        except Exception as e:
            print('Database:\n\tMark Error:{}'.format(str(e)))


    def run(self,thread_counts=16):
        unfinished_items = self.get_unfinished_items(1000)
        self.drivers_pool = DriversPool(size=thread_counts,visual=False)
        task_pool = ThreadPool(thread_counts)
        task_pool.map(self.generate,unfinished_items)
        task_pool.close()
        task_pool.join()


if __name__=='__main__':
    from WatchDog import get_prev_procs
    for proc in get_prev_procs(grep='phantom'):
        print(proc.name)
        print('killing {} ...'.format(proc.pid))
        os.kill(proc.pid,9)

    IEEE_pdf_url_generator().run(thread_counts=8)