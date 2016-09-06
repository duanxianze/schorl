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

from PdfUrlGenerator import *
from src.journal_parser.IEEE_Parser import IEEE_HTML_Parser,Article,get_pdf_link

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
                sql = "update articles set pdf_temp_url = '{}' where google_id = '{}'".format(pdf_page_url,self.google_id)
                cur.execute(sql)
            except Exception as e:
                print('get_pdf_url()_update_pdf_temp_url:{}'.format(str(e)))
                print('Except SQL is {}'.format(sql))
            return get_pdf_link(pdf_page_url,self.driver)


def get_ieee_pdf_url_func(driver,unfinished_item):
    pdf_temp_url = unfinished_item[2]
    if pdf_temp_url:
        return get_pdf_link(pdf_temp_url,driver)
    else:
        return IEEE_Search_Model(
            title = unfinished_item[0],
            google_id = unfinished_item[1],
        ).get_pdf_url()


class IEEE_pdf_url_generator(PdfUrlGenerator):
    def __init__(self,limit=1000):
        PdfUrlGenerator.__init__(self,
            query_sql = "select title,google_id,pdf_temp_url from articles where resource_link is null\
                    and journal_temp_info like '%ieee%' limit {}".format(limit)
        )

    def generate(self,unfinished_item):
        #从title出发，反馈pdf_url给db
        return self._generate(unfinished_item,
            google_id_index = 1,
            get_pdf_url_func = get_ieee_pdf_url_func
        )

    def run(self,thread_counts=16,visual=True):
        self._run(thread_counts,visual)
        self._task_thread_pool.map(self.generate,self._get_unfinished_items())
        self._task_thread_pool.close()
        self._task_thread_pool.join()


if __name__=='__main__':
    from src.crawl_tools.WatchDog import get_prev_procs
    visual=True
    if visual:
        for proc in get_prev_procs(grep='chrome'):
            print(proc.name)
            print('killing {} ...'.format(proc.pid))
            os.kill(proc.pid,9)
    else:
        for proc in get_prev_procs(grep='phantom'):
            print(proc.name)
            print('killing {} ...'.format(proc.pid))
            os.kill(proc.pid,9)

    IEEE_pdf_url_generator(limit=100).run(thread_counts=4,visual=True)