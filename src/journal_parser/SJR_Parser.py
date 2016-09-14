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
import time


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
        print('open_access:{}'.format(self.open_access))

    @property
    def is_saved(self):
        cur.execute(
            "select sjr_id from journal where sjr_id = {}"\
                .format(self.sjr_id)
        )
        return cur.fetchall()

    def save_to_db(self,cur,category_sjr_id):
        self.show_in_cmd()
        if None in (self.name,self.sjr_id,self.open_access):
            return False
        if not self.is_saved:
            try:
                cur.execute(
                    'insert into journal(name,sjr_id,open_access)'
                    'values(%s,%s,%s)',
                    (self.name,self.sjr_id,self.open_access)
                )
                self.save_category_journal(category_sjr_id,self.sjr_id)
            except Exception as e:
                print('[ERROR]:RankJournal:save_to_db:{}'.format(str(e)))
        else:
            print('RankJournal:{} Already saved...'.format(self.sjr_id))

    def save_category_journal(self,
            category_sjr_id,journal_sjr_id):
        #print(category_sjr_id,journal_sjr_id)
        #注意，这里就不做unique判断了，作为save_to_db的子模块
        cur.execute(
            'insert into journal_category(journal_id,category_id)'
            'values(%s,%s)',
            (journal_sjr_id,category_sjr_id)
        )




class JournalDetailPageParser:
    pass


class DetailJournal:
    def __init__(self):
        pass

    @property
    def h_index(self):
        return

    @property
    def country(self):
        return

    @property
    def issn(self):
        return

    @property
    def publisher_id(self):
        return


    def update_db_journal(self):
        pass

    def save_publisher(self):
        pass





if __name__=="__main__":
    from selenium import webdriver
    from src.db_config import cur
    category_id = 1101
    for sec in  JournalRankPageParser(
        area_id = 1100,
        category_id = category_id,
        driver = webdriver.Chrome()
    ).secs:
        journal = RankJournal(sec)
        journal.save_to_db(cur,category_id)
        #print(sec.text)
        print('----------')