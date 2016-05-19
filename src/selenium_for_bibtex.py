#coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#from parse_html import ParseHTML
import time

class CrawlGoogleScholar:

    def setUp(self):
        self.driver = webdriver.Firefox()

    def search_in_google_scholar(self,keyword):
        self.driver.get("https://scholar.google.com/")
        elem = self.driver.find_element_by_id("gs_hp_tsi")
        elem.send_keys(keyword)
        elem.send_keys(Keys.RETURN)
        
    def get_bibtex_url_list(self):
        bibtex_url_list = []
        time_gap = 2
        cite_elem = self.driver.find_element_by_id('gs_md_w')
        elems_list = self.driver.find_elements_by_xpath("//a[@class='gs_nph']")
        for elem in elems_list:
            time.sleep(time_gap)#减少IP被封概率的时间间隔
            if elem.text == u'引用':
                elem.location_once_scrolled_into_view#屏幕滚动
                elem.click()#加载引用页面
                time.sleep(time_gap)#点击后需要等待加载元素完全display再去搜索
                if cite_elem.is_displayed():
                    bibtex_elem = self.driver.find_element_by_class_name('gs_citi')
                    url = bibtex_elem.get_attribute('href')
                    print(url)
                    bibtex_url_list.append(url)
                else:
                    print('时间间隔太短，请调整')
                close_elem = self.driver.find_element_by_id('gs_cit-x')
                close_elem.click()
        return bibtex_url_list
        
    def tearDown(self):
        self.driver.close()
        
if __name__ == "__main__":
    spider = CrawlGoogleScholar()
    spider.setUp()
    spider.search_in_google_scholar('wenhuayu')
    bibtext_list = spider.get_bibtex_url_list()
    spider.tearDown()
    print bibtext_list