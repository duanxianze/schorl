#coding:utf-8
"""
@file:      SJR_Parser
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-14 17:51
@description:
        SJR是罗列各领域杂志社的站点，
        该文件对某领域的杂志社排名页，以及杂志社详情页做解析
"""
import time,requests
from db_config import DB_CONNS_POOL
from bs4 import BeautifulSoup
from crawl_tools.ua_pool import get_one_random_ua
from crawl_tools.request_with_proxy import request_with_random_ua

class SJR_Searcher:
    def __init__(self,keyword=None):
        self.keyword = keyword
        if keyword:
            self.url = 'http://www.scimagojr.com/journalsearch.php?q={}'.format(keyword)
        else:
            self.url = 'http://www.scimagojr.com/journalrank.php'

    @property
    def page_amount(self):
        if self.keyword:
            self.result_amount = SearchPageParser(
                html_source = request_with_random_ua(self.url).text
            ).result_amount
        else:
            self.result_amount = RankPageParser(self.url).result_amount
        return int(self.result_amount/50) + 1

    @property
    def urls(self):
        urls = []
        for page_index in range(1,self.page_amount+1):
            url = self.url + '?&page={}&total_size={}'\
                .format(page_index,self.result_amount)
            urls.append(url)
        return urls

class SearchPageParser:
    def __init__(self,html_source):
        self.soup = BeautifulSoup(html_source,'lxml')

    @property
    def sections(self):
        return self.soup.select('.search_results > a')

    @property
    def result_amount(self):
        return int(self.soup.select_one('.pagination').text.split(' ')[-1])


class PublisherJournal:
    def __init__(self,sec):
        self.unit = sec
        self.cur = DB_CONNS_POOL.new_db_cursor()

    @property
    def name(self):
        return self.unit.select_one('.jrnlname').text

    @property
    def sjr_id(self):
        return int(self.unit['href'].\
            split('?')[-1].split('&')[0].split('=')[-1])

    def show_in_cmd(self):
        print('**********New Journal**********')
        print('name:\t{}'.format(self.name))
        print('sjr_id:\t{}'.format(self.sjr_id))

    def save_to_db(self):
        try:
            self.cur.execute(
                'insert into journal(name,sjr_id)'
                'values(%s,%s)',
                (self.name,self.sjr_id)
            )
            self.show()
        except Exception as e:
            print(str(e))


class RankPageParser:
    def __init__(self,url,area_id=None,category_id=None,driver=None):
        self.url = url
        if category_id and area_id:
            self.url += '?area={}&category={}&order=tr&type=j'.format(area_id,category_id)
        if driver:
            driver.get(self.url)
            time.sleep(2)
            self.soup = BeautifulSoup(driver.page_source,'lxml')
        else:
            resp = request_with_random_ua(self.url,timeout=20)
            self.soup = BeautifulSoup(resp.text,'lxml')

    @property
    def sections(self):
        return self.soup.select('tr')[1:]

    @property
    def result_amount(self):
        return int(self.soup.select_one('.pagination').text.split(' ')[-1])


class RankJournal:
    def __init__(self,sec):
        self.sec = sec
        self.tit = sec.select_one('.tit')
        self.cur = DB_CONNS_POOL.new_db_cursor()

    @property
    def sjr_id(self):
        for kv in self.tit.select_one('a')['href'].split('?')[-1].split('&'):
            key = kv.split('=')[0]
            value = kv.split('=')[1]
            if key == 'q':
                return int(value)

    @property
    def name(self):
        return self.tit.select_one('a').text

    @property
    def open_access(self):
        try:
            self.sec.select_one('.openaccessicon')
            return True
        except Exception as e:
            #print(str(e))
            return False

    def show_in_cmd(self):
        print('***********New RankJournal*********************')
        print('name:{}'.format(self.name))
        print('sjr_id:{}'.format(self.sjr_id))
        print('open_access:{}'.format(self.open_access))

    def is_saved(self,sjr_id):
        cur = self.cur
        cur.execute(
            "select sjr_id from journal where sjr_id = {}"\
                .format(sjr_id)
        )
        return cur.fetchall()

    def is_saved_cj_relation(self,category_sjr_id,journal_sjr_id):
        cur = self.cur
        sql = 'select count(*) from journal_category\
             where category_id={} and journal_id={}'\
                .format(category_sjr_id,journal_sjr_id)
        #print(sql)
        cur.execute(sql)
        amount = cur.fetchall()[0][0]
        return amount

    def save_to_db(self,category_sjr_id=None):
        sjr_id = self.sjr_id
        if None in (self.name,sjr_id,self.open_access):
            return False
        try:
            self.cur.execute(
                'insert into journal(name,sjr_id,open_access)'
                'values(%s,%s,%s)',
                (self.name,sjr_id,self.open_access)
            )
            print('********New journal info***********')
            self.show_in_cmd()
        except Exception as e:
            print(str(e))
            #print('{} [ERROR] in RankJournal: {} Already saved...'.format(category_sjr_id,self.sjr_id))
        if category_sjr_id:
            #关系表在journal表后存
            self.save_category_journal(category_sjr_id,sjr_id)
        self.cur.close()

    def save_category_journal(self,
            category_sjr_id,journal_sjr_id):
        if not self.is_saved_cj_relation(category_sjr_id,
                journal_sjr_id = self.sjr_id):
            self.cur.execute(
                'insert into journal_category(journal_id,category_id)'
                'values(%s,%s)',
                (journal_sjr_id,category_sjr_id)
            )
        else:
            print('RankJournal:\n\t[{},{}] relation saved before'\
                  .format(category_sjr_id,journal_sjr_id))


class JournalDetailPageParser:
    def __init__(self,journal_sjr_id):
        url = 'http://www.scimagojr.com/journalsearch.php?q={}&tip=sid&clean=0'.format(journal_sjr_id)
        print(url)
        resp = request_with_random_ua(url)
        self.journal_id = journal_sjr_id
        self.soup = BeautifulSoup(resp.text,'lxml')
        self.trs = self.soup.find('tbody').find_all('tr')
        self.info_dict = {}
        for tr in self.trs:
            tds = tr.find_all('td')
            self.info_dict[tds[0].text] = tds[1]
        #print(self.info_dict.keys())
        self.cur = DB_CONNS_POOL.new_db_cursor()

    @property
    def h_index(self):
        return int(self.soup.select('.hindexnumber')[0].text)

    @property
    def country(self):
        return self.info_dict['Country'].text

    @property
    def issn(self):
        return self.info_dict['ISSN'].text.split(',')[0]

    @property
    def publisher(self):
        return self.info_dict['Publisher'].text

    @property
    def site_source(self):
        if 'Scope' in self.info_dict.keys():
            return self.info_dict['Scope'].find('a')['href']
        else:
            return None

    @property
    def area_sjr_ids(self):
        a_tags = self.info_dict['Subject Area'].select('a')
        return list(map(lambda x:int(x['href'].split('=')[-1]),a_tags))

    @property
    def category_sjr_ids(self):
        a_tags = self.info_dict['Subject Category'].select('a')
        return list(map(lambda x:int(x['href'].split('=')[-1]),a_tags))

    def show_in_cmd(self):
        print('************New Update********************')
        print('journal_id:{}'.format(self.journal_id))
        print('h_index:{}'.format(self.h_index))
        print('country:{}'.format(self.country))
        print('issn:{}'.format(self.issn))
        print('site_source:{}'.format(self.site_source))
        print('publisher:{}'.format(self.publisher))
        print('area_sjr_ids:{}'.format(self.area_sjr_ids))
        print('category_sjr_ids:{}'.format(self.category_sjr_ids))

    def is_saved_journal_area(self,journal_sjr_id,area_sjr_id):
        self.cur.execute(
            'select count(*) from journal_area WHERE journal_id={} and area_id={}'\
                .format(journal_sjr_id,area_sjr_id)
        )
        return self.cur.fetchall()[0][0]

    def is_saved_journal_category(self,journal_sjr_id,category_sjr_id):
        self.cur.execute(
            'select count(*) from journal_category WHERE journal_id={} and category_id={}'\
                .format(journal_sjr_id,category_sjr_id)
        )
        return self.cur.fetchall()[0][0]

    def save_journal_area(self):
        #保存journal和area的关系到关联表
        journal_sjr_id = self.journal_id
        for area_sjr_id in self.area_sjr_ids:
            if self.is_saved_journal_area(journal_sjr_id,area_sjr_id):
                print('JournalDetailPageParser:\n\t[Error] The relation[{},{}]saved before'\
                      .format(journal_sjr_id,area_sjr_id))
                continue
            self.cur.execute(
                'insert into journal_area(journal_id, area_id)'
                'VALUES (%s,%s)',
                (journal_sjr_id,area_sjr_id)
            )
            print('JournalDetailPageParser:\n\t[Success] The relation[{},{}] saved ok!!'\
                      .format(journal_sjr_id,area_sjr_id))

    def save_journal_category(self):
        print(self.category_sjr_ids)
        try:
            for category_sjr_id in self.category_sjr_ids:
                if self.is_saved_journal_category(self.journal_id,category_sjr_id):
                    print('JournalDetailPageParser:\n\t[Error] The relation[{},{}]saved before'\
                      .format(self.journal_id,category_sjr_id))
                    continue
                self.cur.execute(
                    'insert into journal_category(journal_id, category_id)'
                    'VALUES (%s,%s)',
                    (self.journal_id,category_sjr_id)
                )
                print('JournalDetailPageParser:\n\t[Success] The relation[{},{}] saved ok!!'\
                          .format(self.journal_id,category_sjr_id))
            return True
        except Exception as e:
            print('save_journal_category:{}'.format(str(e)))
            return False

    def update_db_journal(self):
        self.cur.execute(
            'UPDATE journal SET publisher=%s,h_index=%s\
              ,country=%s,issn=%s,site_source=%s,is_crawled=%s WHERE sjr_id = %s',
            (self.publisher,self.h_index,self.country,\
                self.issn,self.site_source,True,self.journal_id)
        )
        print('{} update ok '.format(self.journal_id))

    def save_new_info(self):
        self.save_journal_area()
        self.save_journal_category()
        self.update_db_journal()

