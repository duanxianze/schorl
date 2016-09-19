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
from src.db_config import new_db_cursor
from bs4 import BeautifulSoup
from src.crawl_tools.ua_pool import get_one_random_ua

class JournalRankPageParser:
    def __init__(self,area_id,category_id,driver):
        self.url = 'http://www.scimagojr.com/journalrank.php?area={}&category={}&order=tr&type=j'.format(area_id,category_id)
        driver.get(self.url)
        self.driver = driver
        time.sleep(2)

    @property
    def secs(self):
        return self.driver.find_element_by_xpath(
            '/html/body/div[6]/div[7]/table/tbody'
        ).find_elements_by_tag_name('tr')


class RankJournal:
    def __init__(self,sec):
        self.sec = sec
        self.tit = sec.find_element_by_class_name('tit')
        self.cur = new_db_cursor()

    @property
    def sjr_id(self):
        for kv in self.tit.find_element_by_tag_name('a')\
            .get_attribute('href').split('?')[-1].split('&'):
            key = kv.split('=')[0]
            value = kv.split('=')[1]
            if key == 'q':
                return int(value)

    @property
    def name(self):
        return self.tit.find_element_by_tag_name('a').text

    @property
    def open_access(self):
        try:
            self.sec.find_element_by_class_name('openaccessicon')
            return True
        except Exception as e:
            #print(str(e))
            return False

    def show_in_cmd(self):
        print('name:{}'.format(self.name))
        print('sjr_id:{}'.format(self.sjr_id))
        #print('open_access:{}'.format(self.open_access))

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


    def save_to_db(self,category_sjr_id):
        sjr_id = self.sjr_id
        if None in (self.name,sjr_id,self.open_access):
            return False
        if not self.is_saved(sjr_id):
            self.cur.execute(
                'insert into journal(name,sjr_id,open_access)'
                'values(%s,%s,%s)',
                (self.name,sjr_id,self.open_access)
            )
            print('********New journal info***********')
            self.show_in_cmd()
        else:
            print('{} [ERROR] in RankJournal: {} Already saved...'.format(category_sjr_id,self.sjr_id))
        #关系表在journal表之后存
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
        #print(url)
        resp = requests.get(url,
            headers = {'User-Agent':get_one_random_ua()}
        )
        self.journal_id = journal_sjr_id
        self.soup = BeautifulSoup(resp.text,'lxml')
        self.trs = self.soup.find('tbody').find_all('tr')
        self.info_dict = {}
        for tr in self.trs:
            tds = tr.find_all('td')
            self.info_dict[tds[0].text] = tds[1]
        #print(self.info_dict.keys())
        self.cur = new_db_cursor()

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

if __name__=="__main__":
    jdp = JournalDetailPageParser(journal_sjr_id=25208)
    jdp.show_in_cmd()
