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
import os,sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from journal_parser.GoogleScholar_Parser import ParseHTML,Article
from crawl_tools.request_with_proxy import request_with_proxy


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

    def parse(self,file_name):
        print('--------{}----------'.format(file_name))
        whole_page_success = True
        for sec in ParseHTML(
            from_web=False,
            file_name=self.folder+file_name
        ).sections():
            article = Article(sec)
            if not article.save_to_db(cur):
                print('**************ERROR Article Info******************')
                article.show_in_cmd()
                print('**************ERROR Article Info******************')
                if 'User pro' not in article.title:
                    whole_page_success = False
        if whole_page_success:
            os.remove(self.folder+file_name)
            print('del {} ok'.format(self.folder+file_name))
        print('-------page out-----------')



def run(file_name):
    test = GoogleScholarParserTest('123','./html_results/')
    #test.generate_htmls()
    test.parse(file_name=file_name)


if __name__=="__main__":
    from db_config import cur
    Folder = '../html_results/'
    print(os.listdir(Folder))

    for file_name in os.listdir(Folder):
        run(file_name)


