#coding:utf-8
"""
@file:      update_dynamic_data.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    2.7
@editor:    PyCharm
@create:    2016-08-06 14:08
@description:
            回溯更新articles表的动态数据
"""
from crawl_tools.request_with_proxy import request_with_proxy
from journal_parser.GoogleScholar_Parser import ParseHTML
import time,psycopg2
import platform

'''设置数据库'''
DB_NAME = "sf_development"
USER = "gao"
PASSWORD = "gaotongfei13"
'''连接数据库'''
conn = psycopg2.connect("dbname={0} user={1} password={2}".format(DB_NAME, USER, PASSWORD))
conn.autocommit = True  #设置数据库自动提交
cur = conn.cursor()


class ArticleUpdate(object):
    '''本类用于文章更新'''
    def __init__(self,title,google_id):
        self.title = title
        self.google_id = google_id
        self.url = 'https://scholar.google.com/scholar?start=0&q='+title+'&hl=en&as_sdt=0,5'
        #只需要第一页结果即可
        if platform.system()=='Windows':
            no_proxy_test = True
        else:
            no_proxy_test = False
        self.parse_model = ParseHTML(url=self.url,no_proxy_test=no_proxy_test)


    def get_sec(self):
        '''得到google_id匹配的文章sec结果'''
        p = self.parse_model
        for sec in p.sections():
            if p.google_id(sec)==self.google_id:
                return sec
        return False


    def show_article_status(self):
        '''展示文章条目的各项状态'''
        try:
            cur.execute(
                'select citations_count,citations_link,resource_type,resource_type from articles where google_id="%s"',
                (self.google_id)
            )
            print(cur.fetchall())
        except Exception as e:
            print('show():'+str(e))

        
    def update(self):
        p = self.parse_model
        sec = self.get_sec()
        if sec:
            try:
                '''更新动态数据，有必要需加时间轴，考虑换数据库之类'''
                local_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                citations_count = p.citations_count(sec)
                citations_link = p.citations_link(sec)
                resource_type = p.resource_type(sec)
                resource_link = p.resource_link(sec)
                print(local_time,citations_count,citations_link,resource_type,resource_link,self.google_id)
                print('update before:')
                self.show_article_status()
                '''
                cur.execute(
                    'UPDATE articles SET citations_count = %s , citations_link = "%s" , resource_type = "%s" , resource_link = "%s" WHERE google_id = "%s"',
                    (citations_count,citations_link,resource_type,resource_link,self.google_id)
                )
                print('update ok:')
                '''
                self.show_article_status()
            except Exception as e:
                print ('update():'+str(e))
        else:
            print({
                'title':    self.title,
                'google_id':self.google_id,
                'url':      self.url
            })
            raise Exception(
                'update(): Can not search the article!'
            )


if __name__=='__main__':
    cur.execute(
        'select title,google_id from articles'
    )
    titles = cur.fetchall()
    '''得到数据库已有文章的title集，传入更新模型'''
    for data in titles:
        print(data)
        AU = ArticleUpdate(title=data[0],google_id=data[1])
        try:
            AU.update()
        except:
            print('search failed..')
    cur.close()
    conn.close()
