#coding:utf-8
'''
    parse_html.py 用于解析学者搜索结果页
'''
from bs4 import BeautifulSoup
import requests,random
requests.packages.urllib3.disable_warnings()
from random import randint
from request_with_proxy import request_with_proxy
from ua_pool import agents


def except_or_none(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            print('ArticleParser:\n\tError in {}(): {}'.format(func.__name__,str(e)))
            return None
    return wrapper


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
            #print("from web")
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
        self.soup = BeautifulSoup(self.html,'lxml')
        self.html_text = self.soup.text
        self.rand_port = lambda x, y: randint(x, y)
        self.ua = random.choice(agents)

    def sections(self):
        '''得到文章列表'''
        sections = None
        try:
            sections = self.soup.select('.gs_r')
        except Exception as e:
            print("ERROR:ParseHTML:sections")
        return sections


class Article:
    def __init__(self,sec):
        self.sec = sec
    
    @property
    @except_or_none
    def title(self):
        return self.sec.select('.gs_rt > a')[0].text
    
    @property
    @except_or_none
    def year(self):
        return self.sec.select('.gs_a')[0].text.split('-')[-2].split(',')[-1][1:-1]
    
    @property
    @except_or_none
    def citations_count(self):
        return int(self.sec.select('.gs_fl > a')[0].text[9:])
    
    @property
    @except_or_none
    def citations_link(self):
        return self.sec.select('.gs_fl > a')[0]['href']

    @property
    @except_or_none
    def link(self):
        return self.sec.select('.gs_rt > a')[0]['href']

    @property
    @except_or_none
    def resource_type(self):
        return self.sec.select('.gs_ggsS')[0].text.split(' ')[1][1:-1]

    @property
    @except_or_none
    def resource_link(self):
        if self.resource_type:
            return self.sec.select('.gs_md_wp > a')[0]['href']
        else:
            return None
    
    @property
    @except_or_none
    def summary(self):
        return self.sec.select('.gs_rs')[0].text

    @property
    @except_or_none
    def google_id(self):
        return self.sec.select('.gs_nph > a')[0]['onclick'].split('(')[-1].split(',')[0][1:-1]

    @property
    @except_or_none
    def index(self):
        return self.sec.select('.gs_nph > a')[0]['onclick'].split('(')[-1].split(',')[1][1:-2]

    def save_to_db(self,cur):
        try:
            cur.execute(
                "insert into articles (title, year, citations_count, citations_link, link, resource_type, resource_link, summary, google_id) "
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s) on conflict do nothing",
                (self.title, self.year, self.citations_count, self.citations_link, self.link, self.resource_type, self.resource_link, self.summary, self.google_id)
            )
            self.show_in_cmd()
        except Exception as e:
            print('Article save error:{}'.format(str(e)))

    def show_in_cmd(self):
        print('**************New Article Info******************')
        print('title:\t\t{}'.format(self.title))
        print('google_id:\t{}'.format(self.google_id))
        print('year:\t\t{}'.format(self.year))
        print('citations_count:\t{}'.format(self.citations_count))
        print('resource_type:\t{}'.format(self.resource_type))
        print('resource_link:\t{}'.format(self.resource_link))
        print('citations_link:\t{}'.format(self.citations_link))
        print('link:\t\t\t{}'.format(self.link))
        print('summary:\t\t{}'.format(self.summary))
        print('**************New Article Info******************')



if __name__=='__main__':
    for sec in ParseHTML(from_web=False).sections():
        Article(sec).show_in_cmd()