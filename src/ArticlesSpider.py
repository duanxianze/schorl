#coding:utf-8
"""
@file:      ArticlesSpider.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-20 23:44
@description:
            --
"""
from math import ceil
from parse_html import *
from multiprocessing.dummy import Pool as ThreadPool
import re,random,os,psycopg2

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

class ArticleSpider:
    '''
        文章爬虫类，爬取Google Scholar
    '''
    def __init__(self):
        pass

    @property
    def unfinished_items(self):
        #从scholar表中检索出未爬取过的学者集
        cur.execute(
            "select id, first_name, middle_name, last_name from scholars"
        )
        return cur.fetchall()
    
    @property
    def counts_of_unfinished_item(self):
        cur.execute(
            "select count(*) from scholars where is_added = 0"
                )
        return int(cur.fetchall[0][0])

    def crawl(self,unfinished_item):
        print(unfinished_item)
        #对于单条学者item的爬取处理
        try:
            scholar_db_id = unfinished_item[0]
            full_name = unfinished_item[1:]
            for page_url in ScholarSearch(full_name).page_urls():
                for sec in ParseHTML(url=page_url).sections():
                    Article(sec).save_to_db(cur)
            cur.execute("update scholars set is_added = 1 where id = (%s)", (scholar_db_id,))
        except Exception as e:
            print('ArticleSpider:\n\tERROR:{}'.format(str(e)))
        '''
        scholar_db_id = unfinished_item[0]
        full_name = unfinished_item[1:]
        for page_url in  ScholarSearch(full_name).page_urls():
            for sec in ParseHTML(page_url).sections():
                Article(sec).save_to_db(cur)
        cur.execute("update scholars set is_added = 1 where id = (%s)", (scholar_db_id,))
        '''

    def run(self,thread_counts=4,shuffle=True):
        pool = ThreadPool(thread_counts)
        unfinished_items = self.unfinished_items
        if shuffle:
            random.shuffle(unfinished_items)#打乱顺序
        pool.map(self.crawl, unfinished_items)
        #主循环，对于检索的结果列表中每个item都交给crawl函数执行
        pool.close()
        pool.join()



class ScholarSearch:
    def __init__(self,name):
        '''
            传入参数：
                name:       从学者表中检索出的学者名字元组，包含first_name, middle_name, last_name
            包含属性：
                self.name:        学者姓名元组
                self.full_name :  学者完整姓名，将上方姓名元组整合得到
                self.start_url :  搜索学者姓名，其结果的起始url
        '''
        self.name = name
        if self.name[1].strip()=='':
            '''
                对于full_name的运算，若middle_name不存在，需要区分对待
            '''
            self.full_name = self.name[0].strip() + ' ' + self.name[2].strip()
            self.start_url = 'https://scholar.google.com/scholar?start=0&q='+self.full_name+'&hl=en&as_sdt=0,5'
        else:
            self.full_name = self.name[0].strip() + ' ' + self.name[1].strip() + ' ' + self.name[2].strip()
            self.start_url = 'https://scholar.google.com/scholar?start=0&q='+self.full_name+'&hl=en&as_sdt=0,5'

    def page(self):
        '''
            访问通过start_url，解析页面元素，得到文章数量
            算出该学者搜索结果的页数，作为返回值
        '''
        p = 10
        r = request_with_proxy(self.start_url)
        if r:
            '''如果有返回结果'''
            soup = BeautifulSoup(r.text, "lxml")
            about = soup.select("#gs_ab_md")
            if about:
                result = about[0].text
                result_num = re.findall("About\s+([\w\,]+)\s+results", result)
                if result_num:
                    '''找到文章数，算出总页数'''
                    result_num = result_num[0].replace(",", "")
                    p = int(ceil(int(result_num)/float(10)))#ceil取整
        return p

    def page_urls(self):
        '''
            得到搜索结果页数，
            并生成每页url的集合，作为返回值
        '''
        pages = self.page()
        if pages>10:
            pages = 10
        '''10页以后意义不大，故大于10页取10页爬取'''
        urls = ['https://scholar.google.com/scholar?start={0}&q={1}&hl=en&as_sdt=0,5'.format(p*10-10, self.full_name) for p in range(1, pages+1)]
        return urls


if __name__=='__main__':
    ArticleSpider().run(thread_counts=8)
    #直接运行本文件，没有看门狗功能，请运行articles_wacthdog.py,
    #进程运行一段时间，增量长时间为零，不能自动控制重启
    #由看门狗parent process调用本文件，作为sub process，控制并监测运行情况








