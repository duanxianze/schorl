#coding:utf-8
"""
@file:      ElsevierSpider.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-17 19:56
@description:
            Elsevier针对某特定journal获取其古往今来的所有文章的爬虫
            上级模块有多线程分配，故此处用单线程写
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

import re
from bs4 import BeautifulSoup
from Journals_Task.JournalSpider import JournalSpider
from crawl_tools.request_with_proxy import request_with_random_ua
from journal_parser.Elsevier_Parser import ElsevierAricle,ElsevierAllItemsPageParser
from crawl_tools.decorators import except_return_none
ERN_METHOD = lambda func:except_return_none(func,'ElsevierSpider')


class ElsevierSpider(JournalSpider):
    '''
        sample_url: http://www.sciencedirect.com/science/journal/15708268
    '''
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.JournalObj = JournalObj
        print('origin url',self.url)
        self.handle_sciencedirect_url()
        print('finish url',self.url)
        self.generate_volume_links()

    @ERN_METHOD
    def handle_sciencedirect_url(self):
        #print(self.url)
        if 'sciencedirect' in self.url:
            return
        resp = request_with_random_ua(self.url)
        soup = BeautifulSoup(resp.text,'lxml')
        print('---------------------')
        if soup.find_all(text='404'):
            raise Exception('404')
        temp_url = soup.select_one('.cta-primary')['href']
        temp_url2 = soup.find_all("a",href=re.compile("guide-for-authors"))
        if temp_url2:
            temp_url2 = temp_url2[0]['href']
        print('temp_url:{}'.format(temp_url))
        print('temp_url2:{}'.format(temp_url2))
        for url in [temp_url2,temp_url]:
            try:
                journal_index = url.split('/')[0].split('-')
                self.url = 'http://www.sciencedirect.com/science/journal/{}'\
                    .format(journal_index[0]+journal_index[1])
                return
            except Exception as e:
                continue
                print(str(e))

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            pass
        #假如数据库中已保存，直接读取即可，无需生成
        for volume_area_link in ElsevierAllItemsPageParser(
            html_source = request_with_random_ua(self.url).text
        ).volume_area_links:
            #先分volume年份区间（十年）
            #print('Elsevier Volume Area link:%s'%volume_area_link)
            area_volume_links = ElsevierAllItemsPageParser(
                html_source = request_with_random_ua(volume_area_link).text
            ).volume_links
            area_volume_links.append(volume_area_link)
            #得到该区间所有年份的page_url
            self.volume_links.extend(area_volume_links)

    def run(self,internal_thread_cot=8):
        self._run(
            AllItemsPageParser = ElsevierAllItemsPageParser,
            JournalArticle = ElsevierAricle,
            check_pdf_url=False,
            internal_thread_cot=internal_thread_cot,
        )

