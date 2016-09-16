# coding:utf-8
"""
@file:      Elsevier_Parser.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-06 12:16
@description:
            用于解析elsevier出版社的文章详情页
            域名：http://www.sciencedirect.com/science/article/pii/xxxx
"""

from bs4 import BeautifulSoup


class Elsevier_Parser:

    def __init__(self, article_page_url, driver):
        driver.get(article_page_url)
        if 'sciencedirect' not in article_page_url:
            raise Exception(
                '[Error] in Elsevier_Parser:\n\tUrl pattern is wrong.')
        self.soup = BeautifulSoup(driver.page_source, 'lxml')
        self.__keywords = ''

    @property
    def pdf_url(self):
        try:
            link = self.soup.select_one("#pdfLink")['href']
            if 'ShoppingCartURL' in link:
                # 被指向支付页面，不是在学校ip里的情况
                return None
            else:
                return link
        except Exception as e:
            print('[Error] in Elsevier_Parser.pdf_url():{}'.format(str(e)))
            #print('The url of issue is:{}\n'.format(link))
            return None

    @property
    def keywords(self):
        keywords_locate = None
        try:
            keywords_locate = self.soup.find_all(class_='keyword')
            for i in keywords_locate:
                self.__keywords = self.__keywords + \
                    '{}, '.format(i.get_text().replace(';', ', '))
        except:
            pass
        if self.__keywords:
            return self.__keywords, 'Acquired'
        else:
            return None, 'Keywords not found'


if __name__ == "__main__":
    ep = Elsevier_Parser(
        article_page_url='http://www.sciencedirect.com/science/article/pii/S1090780708001389'
    )
    print(ep.pdf_url)
