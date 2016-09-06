#coding:utf-8
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
    def __init__(self,article_page_url,driver):
        driver.get(article_page_url)
        self.soup = BeautifulSoup(driver.page_source,'lxml')

    @property
    def pdf_url(self):
        try:
            link = self.soup.select_one("#pdfLink")['href']
            if 'ShoppingCartURL' in link:
                #被指向支付页面，不是在学校ip里的情况
                return None
            else:
                return link
        except:
            return None


if __name__=="__main__":
    ep = Elsevier_Parser(
        article_page_url='http://www.sciencedirect.com/science/article/pii/S1090780708001389'
    )
    print(ep.pdf_url)