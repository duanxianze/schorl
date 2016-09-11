#coding:utf-8
"""
@file:      main_spider_test.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-10 18:06
@description:
            --
"""
from journal_parser.GoogleScholar_Parser import ParseHTML,Article
from crawl_tools.request_with_proxy import request_with_proxy
import os

class GoogleScholarParserTest:
    def __init__(self,name,save_folder):
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        self.folder = save_folder
        self.url = 'http://scholar.google.com/scholar?start=0&q='+name+'&hl=en&lr=lang_en&as_sdt=0,5'
        #self.url = 'http://python.usyiyi.cn/python_278/library/shutil.html'

    def generate_htmls(self):
        for i in range(5):
            print(i)
            resp = request_with_proxy(self.url,no_proxy_test=True)
            with open(
                os.path.join(self.folder, '{}.html'.format(i)), 'wb'
            ) as html_file:
                html_file.write(resp.content)

    def parse(self,file_name,cur):
        print('--------{}----------'.format(file_name))
        for sec in ParseHTML(
            from_web=False,
            file_name=self.folder+file_name
        ).sections():
            article = Article(sec)
            if not article.save_to_db(cur):
                article.show_in_cmd()
        print('-------page out-----------')


if __name__=="__main__":
    from db_config import cur
    Folder = './html_results/'
    print(os.listdir(Folder))
    for name in os.listdir(Folder):
        test = GoogleScholarParserTest(name,Folder)
        #test.generate_htmls()
        test.parse(file_name=name,cur=cur)
