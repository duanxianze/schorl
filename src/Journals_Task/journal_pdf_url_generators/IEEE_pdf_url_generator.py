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
from journal_parser.IEEE_Parser import IEEE_HTML_Parser,Article,get_ieee_pdf_link
from journal_pdf_url_generators.PdfUrlGenerator import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.db_config import new_db_cursor
cur = new_db_cursor()

class IEEE_Search_Model:
    def __init__(self,title,google_id,driver):
        self.title = title
        self.google_id = google_id
        for i in range(10):
            search_result_url = 'http://ieeexplore.ieee.org/search/searchresult.jsp?queryText={}&newsearch=true'\
                    .format('%20'.join(title.split(' ')))
            driver.get(
                url = search_result_url
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
                print('[Error] in IEEE_Search_Model():{}'.format(str(e)))
                print('The url of issue is:{}\nReload again..'.format(search_result_url))
        self.sec = IEEE_HTML_Parser(driver).sections[0]
        self.driver = driver

    def get_pdf_url(self):
        pdf_page_url = Article(self.sec).pdf_page_url
        if pdf_page_url:
            try:
                sql = "update articles set pdf_temp_url = '{}' where google_id = '{}'".format(pdf_page_url,self.google_id)
                cur.execute(sql)
            except Exception as e:
                print('[Error] in get_pdf_url()_update_pdf_temp_url:{}'.format(str(e)))
                print('Except SQL is {}'.format(sql))
            return get_ieee_pdf_link(pdf_page_url,self.driver)


def get_ieee_pdf_url_func(driver,unfinished_item):
    pdf_temp_url = unfinished_item[2]
    if pdf_temp_url:
        return get_ieee_pdf_link(pdf_temp_url,driver)
    else:
        return IEEE_Search_Model(
            title = unfinished_item[0],
            google_id = unfinished_item[1],
            driver=driver
        ).get_pdf_url()


class IEEE_pdf_url_generator(PdfUrlGenerator):
    def __init__(self):
        PdfUrlGenerator.__init__(self)

    def get_unfinished_items(self):
        ret = self._get_unfinished_items(self.query_sql)
        print('IEEE_pdf_url_generator:\n\tGot {} new items in limit {}...'.format(len(ret),self.query_limit))
        return ret

    def generate(self,unfinished_item):
        #从title出发，反馈pdf_url给db
        return self._generate(unfinished_item,
            google_id_index = 1,
            get_pdf_url_func = get_ieee_pdf_url_func
        )

    def run(self,thread_counts=16,visual=True,limit=1000):
        self.query_limit = limit
        self._run(thread_counts,visual)
        self.query_sql = "select title,google_id,pdf_temp_url from articles where resource_link is null\
                    and journal_temp_info like '%ieee%' ORDER by id desc limit {}".format(limit)
        self._task_thread_pool.map(self.generate,self.get_unfinished_items())
        self._close()


if __name__=='__main__':
    from crawl_tools.WatchDog import close_procs_by_keyword

    visual = False

    if visual:
        close_procs_by_keyword(keyword='chrome')
    else:
        close_procs_by_keyword(keyword='phantom')

    IEEE_pdf_url_generator().run(thread_counts=8,visual=visual,limit=1000)