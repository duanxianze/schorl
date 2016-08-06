#coding:utf-8
'''
    parse_html.py 用于解析学者搜索结果页
'''
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
requests.packages.urllib3.disable_warnings()
from random import randint
import socks
import socket
from request_with_proxy import request_with_proxy

class ParseHTML:
    '''
        对于google_scholar的搜索结果页进行解析，包含文章列表，逐一解析
    '''
    def __init__(self, from_web=True, url=None, no_proxy_test=False):
        '''
            from_web和url参数是需要一边爬取一边解析的情况，
            若本地解析html则实例化时不需要传入

            类属性包括:
                self.soup:  BeautifulSoup解析模型生成的文档结构
                self.html_text：soup中包含的text
                self.rand_port：代理端口
                self.ua：       代理实例对象
        '''
        if from_web and url:
            print("from web")
            self.html = request_with_proxy(url,no_proxy_test=no_proxy_test).text
        else:
            print("from local file")
            with open('scholar_articles.htm', 'rb') as f:
                self.html = f.read()
        '''
        # write html
        with open("test.html", "w+") as test:
            test.write(self.html)
        '''
        self.soup = BeautifulSoup(self.html, 'lxml')
        self.html_text = self.soup.text
        self.rand_port = lambda x, y: randint(x, y)
        self.ua = UserAgent()

    '''得到文章列表'''
    def sections(self):
        sections = None
        try:
            sections = self.soup.select('.gs_r')
        except Exception as e:
            print("ERROR:ParseHTML:sections")

        return sections

    def title(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段（由sections裁剪得到）
            返回文章题目
        '''
        title = ''
        try:
            title = sec.select('.gs_rt > a')[0].text
        except Exception as e:
            print("ERROR:ParseHTML:title")
            print(e)
        return title

    def year(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段
            返回文章发表年份
        '''
        year = None
        try:
            year = sec.select('.gs_a')[0].text.split('-')[-2].split(',')[-1][1:-1]
        except Exception as e:
            print("ERROR:ParseHTML:year")
            print(e)
        return year

    def citations_count(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段
            返回文章引用次数
        '''
        citations_count = None
        try:
            citations_count = sec.select('.gs_fl > a')[0].text[9:]
            citations_count = int(citations_count)
        except Exception as e:
            print("ERROR:ParseHTML:citations_count")
            print(e)
        return citations_count

    def citations_link(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段
            返回文章的引用链接，指向引用该文章的搜索结果url
        '''
        citations_link = None
        try:
            citations_link = sec.select('.gs_fl > a')[0]['href']
        except Exception as e:
            print("ERROR:ParseHTML:citations_link")
            print(e)
        return citations_link

    def link(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段
            返回文章链接
        '''
        link = None
        try:
            link = sec.select('.gs_rt > a')[0]['href']
        except Exception as e:
            print("ERROR:ParseHTML:link")
            print(e)
        return link

    # need to config proxy in terminal
    def bibtex(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段
            返回文章bibtex信息
        '''
        bibtex = None
        ajax_url = 'https://scholar.google.co.jp/scholar?q=info:' + self.google_id(sec) +':scholar.google.com/&output=cite&scirp='+ self.index(sec) +'&hl=en'
        ajax_url = 'http' + ajax_url[5:]
        print(ajax_url)
        try:
            ajax_res = request_with_proxy(ajax_url)
            print(ajax_res.status_code)
            ajax_res_cnt = ajax_res.content
            print(ajax_res_cnt)
            '''
            ajax_soup = BeautifulSoup(ajax_res_cnt, 'lxml')
            bibtex_url = ajax_soup.select('.gs_citi')[0]['href']
            bibtex_url = 'http://scholar.google.com' + bibtex_url
            res = request_with_proxy(bibtex_url)
            bibtex = res.content
            '''
        except Exception as e:
            print('ERROR:ParseHTML:bibtex')
            print(e)

        return bibtex

    def resource_type(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段
            返回文章资源类型，多是html或pdf
        '''
        resource_type = None
        try:
            resource_type = sec.select('.gs_ggsS')[0].text.split(' ')[1][1:-1]
        except:
            pass
        return resource_type

    def resource_link(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段
            返回文章资源链接，便于pdf的下载
        '''
        resource_link = None
        try:
            resource_link = sec.select('.gs_md_wp > a')[0]['href']
        except:
            pass
        return resource_link

    def summary(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段
            返回文章内容介绍总结性文字
        '''
        summary = None
        try:
            summary = sec.select('.gs_rs')[0].text
        except Exception as e:
            print("ERROR:ParseHTML:summary")
            print(e)
        return summary

    def google_id(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段
            返回文章在google_scholar中google为其编码的ID
        '''
        google_id = None
        try:
            google_id = sec.select('.gs_nph > a')[0]['onclick'].split('(')[-1].split(',')[0][1:-1]
        except Exception as e:
            print("ERROR:ParseHTML:google_id")
            print(e)
        return google_id

    # number in pages
    def index(self, sec):
        '''
            传入参数：
                sec:每一个文章的片段
            返回文章在该页面是第几个文章
        '''
        index = None
        try:
            index = sec.select('.gs_nph > a')[0]['onclick'].split('(')[-1].split(',')[1][1:-2]
        except Exception as e:
            print("ERROR:ParseHTML:index")
            print(e)
        return index

# instance object
#p = ParseHTML(url='https://scholar.google.com/scholar?hl=en&q=wenhua+yu&btnG=&as_sdt=1%2C5&as_sdtp=')
'''
p = ParseHTML(from_web=False)
for sec in p.sections():
    time.sleep(5)
    print('title',p.title(sec))
    print('year',p.year(sec))
    print('citations_count',p.citations_count(sec))
    print('link',p.link(sec))
    print('resource_type',p.resource_type(sec))
    print('resource_link',p.resource_link(sec))
    print('summary',p.summary(sec))
    print('google_id',p.google_id(sec))
    print('index',p.index(sec))
    #print('bibtex',p.bibtex(sec))
    print("===")
    print(p.citations_link(sec))
'''
