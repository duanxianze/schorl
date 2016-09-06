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
from src.crawl_tools.ua_pool import get_one_random_ua
from selenium import webdriver
from bs4 import BeautifulSoup
import requests


class Elsevier_Parser:
    def __init__(self,article_page_url,driver=None,from_web=True):
        if from_web:
            source = requests.get(
                url=article_page_url,
                headers={'User-Agent':get_one_random_ua()}
            ).text
            if not self.pdf_url:
                #假设requests静态爬虫被封，查不到pdf_url,调用selenium
                driver_need_close = False
                if not driver:
                    #假设使用者未填写driver
                    driver_need_close = True
                    print('Launch temp driver...')
                    driver = webdriver.Chrome()
                driver.get(article_page_url)
                source = driver.page_source
                if driver_need_close:
                    driver.close()
            self.soup = BeautifulSoup(source,'lxml')
        else:
            with open('EPR oximetry in three spatial dimensions using sparse spin distribution.html', 'rb') as f:
                self.soup = BeautifulSoup(f.read(),'lxml')

    @property
    def pdf_url(self):
        try:
            return self.soup.select_one("#pdfLink")['href']
        except:
            return None


if __name__=="__main__":
    ep = Elsevier_Parser(
        #driver=webdriver.Chrome(),
        #from_web = False,
        article_page_url='http://www.sciencedirect.com/science/article/pii/S1090780708001389'
    )
    print(ep.pdf_url)