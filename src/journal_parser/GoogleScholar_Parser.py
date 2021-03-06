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
            本地测试解析时from_web = False
        '''
        if from_web and url:
            #print("from web")
            self.html = request_with_proxy(url,no_proxy_test=no_proxy_test).text
        else:
            print("from local file")
            with open(file_name, 'rb') as f:
                self.html = f.read()
        self.soup = BeautifulSoup(self.html,'lxml')

    @except_or_none
    def sections(self):
        '''得到文章列表'''
        return self.soup.select('.gs_r')



class Article:
    def __init__(self,sec):
        self.sec = sec
    
    @property
    @except_or_none
    def title(self):
        try:
            return self.sec.select('.gs_rt > a')[0].text
        except:
            return self.sec.select('.gs_rt')[0].text

    @property
    @except_or_none
    def year(self):
        try:
            return int(self.sec.select('.gs_a')[0].text.split('-')[-2].split(',')[-1][1:-1])
        except:
            try:
                return int(self.sec.select('.gs_a')[0].text.split(',')[-1].split('-')[0].strip(' '))
            except:
                return -1
    @property
    def citations_count(self):
        try:
            return int(self.sec.select('.gs_fl > a')[0].text.split(' ')[-1])
        except:
            return 0

    @property
    @except_or_none
    def citations_link(self):
        res = self.sec.select('.gs_fl > a')[0]['href']
        if res == '#':
            return None
        else:
            return res


    @property
    @except_or_none
    def link(self):
        return self.sec.select('.gs_rt > a')[0]['href']

    @property
    def resource_type(self):
        try:
            return self.sec.select('.gs_ggsS')[0].text.split(' ')[1][1:-1]
        except:
            return None

    @property
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

    '''
    @property
    @except_or_none
    def journal_temp_info(self):
        # 该属性的创建是由于bibtex获取困难，但目前需要杂志社的信息，识别IEEE直接下载pdf
        # 之前考虑数据不冗余，所以没把bibtex中重复的信息单独作为一项
        # 本属性也只属于articles表临时列，成品可删除
        return self.sec.select('.gs_a')[0].text.split('-')[-1]
    '''

    def is_saved(self,cur):
        cur.execute(
            "select id from articles where google_id = '{}'".format(self.google_id)
        )
        return cur.fetchall()

    def db_item_values(self,cur):
        cur.execute(
            "select citations_count from articles where google_id = '{}'".format(self.google_id)
        )
        return cur.fetchall()[0]

    def save_to_db(self,cur):
        if not self.google_id:
            print('Get google_id Error')
            return False
        if self.is_saved(cur):
            print('"{}" already saved before...'.format(self.google_id))
            if None in self.db_item_values(cur):
                #假如数据库中该item存在空项，则更新
                print('Somthing is null in db,Updating...')
                if self.citations_count is not None:
                    #假如爬虫数据获取正常
                    cur.execute(
                        "update articles set \
                         citations_count = {},citations_link='{}' \
                         where google_id = '{}'".format(
                            self.citations_count,\
                            self.citations_link,self.google_id
                        )
                    )
                    print('Update all methods of {} ok!'.format(self.google_id))
                else:
                    print('Upate Error:Got some methods whose value is null...')
                    return False
            return True
        try:
            if self.title and self.year and self.google_id:
                cur.execute(
                    "insert into articles (title, year, citations_count, citations_link, link, \
                    resource_type, resource_link, summary, google_id) "
                    "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on conflict do nothing",
                    (self.title, self.year, self.citations_count, self.citations_link, self.link, \
                     self.resource_type, self.resource_link, self.summary, self.google_id)
                )
                print('**************New Article Info******************')
                self.show_in_cmd()
                print('**************New Article Info******************')
                return True
            else:
                print('[Insert Error]:Some method is null...')
        except Exception as e:
            if 'User profiles for' not in self.title:
                print('**************ERROR Article Info******************')
                self.show_in_cmd()
                print('**************ERROR Article Info******************')
            print('Article save error:{}'.format(str(e)))
            #print('The except sql is {}'.format(sql))
        return False


    def show_in_cmd(self):
        print('title:\t\t{}'.format(self.title))
        print('google_id:\t{}'.format(self.google_id))
        print('year:\t\t{}'.format(self.year))
        print('citations_count:\t{}'.format(self.citations_count))
        print('resource_type:\t{}'.format(self.resource_type))
        print('resource_link:\t{}'.format(self.resource_link))
        print('citations_link:\t{}'.format(self.citations_link))
        print('link:\t\t\t{}'.format(self.link))
        print('summary:\t\t{}'.format(self.summary))

