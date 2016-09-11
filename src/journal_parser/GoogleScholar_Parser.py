#coding:utf-8
'''
    parse_html.py 用于解析学者英文搜索结果页
'''
from bs4 import BeautifulSoup
from random import randint
from crawl_tools.request_with_proxy import request_with_proxy
from crawl_tools.ua_pool import get_one_random_ua
import requests
requests.packages.urllib3.disable_warnings()

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
    def __init__(self, from_web=True, url=None, no_proxy_test=False,file_name=None):
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
            with open(file_name, 'rb') as f:
                self.html = f.read()
        '''
        # write html
        with open("test.html", "w+") as test:
            test.write(self.html)
        '''
        self.soup = BeautifulSoup(self.html,'lxml')
        self.html_text = self.soup.text
        self.rand_port = lambda x, y: randint(x, y)
        self.ua = get_one_random_ua()

    def sections(self):
        '''得到文章列表'''
        sections = None
        try:
            sections = self.soup.select('.gs_r')
        except Exception as e:
            print("ERROR:ParseHTML:sections:{}".format(str(e)))
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

    @property
    @except_or_none
    def journal_temp_info(self):
        # 该属性的创建是由于bibtex获取困难，但目前需要杂志社的信息，识别IEEE直接下载pdf
        # 之前考虑数据不冗余，所以没把bibtex中重复的信息单独作为一项
        # 本属性也只属于articles表临时列，成品可删除
        return self.sec.select('.gs_a')[0].text.split('-')[-1]


    def is_saved(self,cur):
        cur.execute(
            "select id from articles where google_id = '{}'".format(self.google_id)
        )
        return cur.fetchall()

    def has_journal_temp(self,cur):
        cur.execute(
            "select journal_temp_info from articles where google_id = '{}'".format(self.google_id)
        )
        return cur.fetchall()[0][0]

    def save_to_db(self,cur):
        if self.is_saved(cur):
            print('Article save error: "{}" already saved before.'.format(self.google_id))
            if not self.has_journal_temp(cur):
                if 'ieee' in self.journal_temp_info:
                    #IEEE买了独享资源
                    cur.execute(
                        "update articles set resource_type = 'PDF' where google_id = '{}'".format(self.google_id)
                    )
                print('Get journal temp information: {}'.format(self.journal_temp_info))
                cur.execute(
                    "update articles set journal_temp_info = '{}' where google_id = '{}'".format(self.journal_temp_info,self.google_id)
                )
                print('update_journal ok!')
            return
        try:
            cur.execute(
                "insert into articles (title, year, citations_count, citations_link, link, resource_type, resource_link, summary, google_id,journal_temp_info) "
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on conflict do nothing",
                (self.title, self.year, self.citations_count, self.citations_link, self.link, self.resource_type, self.resource_link, self.summary, self.google_id,self.journal_temp_info)
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
        print('journal_temp_info:\t\t{}'.format(self.journal_temp_info))
        print('**************New Article Info******************')



if __name__=='__main__':
    for sec in ParseHTML(from_web=False).sections():
        #Article(sec).save_to_db(cur)
        #Article(sec).update_journal(cur)
        Article(sec).show_in_cmd()