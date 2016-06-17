#coding:utf-8
'''
    selenium_version_parse.py 用于测试selenium版本的爬取方式
'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 600))
display.start()

class CrawlGoogleScholar:

    def __init__(self,keyword):
        self.driver = webdriver.Firefox()
        self.driver.get("https://scholar.google.com/")
        elem = self.driver.find_element_by_id("gs_hp_tsi")
        elem.send_keys(keyword)
        elem.send_keys(Keys.RETURN)

    def get_sections(self):
        sections = self.driver.find_elements_by_class_name('gs_r')
        return sections

    def bibtex_url(self,sec):
        cite_button = sec.find_elements_by_class_name('gs_nph')[1]
        cite_button.click()
        time.sleep(2) #点击后需要等待加载元素完全display再去搜索
        bibtex_elem = self.driver.find_element_by_class_name('gs_citi')
        bibtex_url = bibtex_elem.get_attribute('href')
        close_elem = self.driver.find_element_by_id('gs_cit-x')
        close_elem.click()
        return bibtex_url

    def title(self, sec):
        title = sec.find_element_by_class_name('gs_rt').find_element_by_tag_name('a').text
        return title

    def year(self, sec):
        year = sec.find_element_by_class_name('gs_a').text.split('-')[-2].split(',')[-1][1:-1]
        return year

    def citations_count(self, sec):
        citations_count = sec.find_element_by_class_name('gs_ri').find_element_by_class_name('gs_fl').find_element_by_tag_name('a').text[6:]
        citations_count = int(citations_count)
        return citations_count

    def link(self, sec):
        link = sec.find_element_by_class_name('gs_rt').find_element_by_tag_name('a').get_attribute('href')
        return link

    def resource_type(self, sec):
        resource_type = None
        try:
            resource_type = sec.find_element_by_class_name('gs_ctg2').text[1:-1]
        except:
            pass
        return resource_type

    def resource_link(self, sec):
        resource_link = None
        try:
            resource_link = sec.find_element_by_id('gs_ggsW1').find_element_by_tag_name('a').get_attribute('href')
        except:
            pass
        return resource_link

    def summary(self, sec):
        summary = sec.find_element_by_class_name('gs_rs').text
        return summary

    def google_id(self, sec):
        google_id = sec.find_elements_by_class_name('gs_nph')[1].get_attribute('onclick').split('(')[-1].split(',')[1][1:-1]
        return google_id

    def tearDown(self):
        self.driver.close()
        display.stop()

if __name__ == "__main__":
    spider = CrawlGoogleScholar(keyword= 'wenhuayu')
    sections = spider.get_sections()
    for sec in sections:
        time.sleep(2)#防止被封的时间间隔
        print('bibtex_url',spider.bibtex_url(sec))
        print('title',spider.title(sec))
        print('year',spider.year(sec))
        print('citations_count',spider.citations_count(sec))
        print('link',spider.link(sec))
        print('resource_type',spider.resource_type(sec))
        print('resource_link',spider.resource_link(sec))
        print('summary',spider.summary(sec))
        print('google_id',spider.google_id(sec))
        print('---------------')
    spider.tearDown()
