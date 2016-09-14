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
                return value

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

    def save_to_db(self):
        #记得最后存关联表
        pass

class JournalDetailPageParser:
    pass


class DetailJournal:
    def update_db_journal(self):
        pass

    def save_publisher_journal(self):
        pass


if __name__=="__main__":
    from selenium import webdriver
    for sec in  JournalRankPageParser(
        area_id = 1100,
        category_id = 1101,
        driver = webdriver.Chrome()
    ).secs:
        journal = RankJournal(sec)
        journal.show_in_cmd()
        print(sec.text)
        print('----------')