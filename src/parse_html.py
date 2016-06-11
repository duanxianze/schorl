from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
requests.packages.urllib3.disable_warnings()
from random import randint
import socks
import socket
from request_with_proxy import request_with_proxy

class ParseHTML:
    def __init__(self, from_web=True, url=None):
        if from_web and url:
            print("from web")
            self.html = request_with_proxy(url).text
        else:
            print("from local file")
            with open('scholar_articles.htm', 'rb') as f:
                self.html = f.read()
        '''
        # write html
        with open("test.html", "w+") as test:
            test.write(self.html)
        '''
        self.soup = BeautifulSoup(self.html, 'lxml')
        self.html_text = self.soup.text
        self.rand_port = lambda x, y: randint(x, y)
        self.ua = UserAgent()
        
    def sections(self):
        sections = None
        try:
            sections = self.soup.select('.gs_r')
        except Exception as e:
            print("ERROR:ParseHTML:sections")

        return sections

    def title(self, sec):
        title = ''
        try:
            title = sec.select('.gs_rt > a')[0].text
        except Exception as e:
            print("ERROR:ParseHTML:title")
            print(e)
        return title

    def year(self, sec):
        year = None
        try:
            year = sec.select('.gs_a')[0].text.split('-')[-2].split(',')[-1][1:-1]
        except Exception as e:
            print("ERROR:ParseHTML:year")
            print(e)
        return year

    def citations_count(self, sec):
        citations_count = None
        try:
            citations_count = sec.select('.gs_fl > a')[0].text[9:]
            citations_count = int(citations_count)
        except Exception as e:
            print("ERROR:ParseHTML:citations_count")
            print(e)
        return citations_count

    def citations_link(self, sec):
        citations_link = None
        try:
            citations_link = sec.select('.gs_fl > a')[0]['href']
        except Exception as e:
            print("ERROR:ParseHTML:citations_link")
            print(e)
        return citations_link

    def link(self, sec):
        link = None
        try:
            link = sec.select('.gs_rt > a')[0]['href']
        except Exception as e:
            print("ERROR:ParseHTML:link")
            print(e)
        return link

    # need to config proxy in terminal
    def bibtex(self, sec):
        bibtex = None
        ajax_url = 'https://scholar.google.co.jp/scholar?q=info:' + self.google_id(sec) +':scholar.google.com/&output=cite&scirp='+ self.index(sec) +'&hl=en'
        ajax_url = 'http' + ajax_url[5:]
        print(ajax_url)
        try:
            ajax_res = request_with_proxy(ajax_url)
            print(ajax_res.status_code)
            ajax_res_cnt = ajax_res.content
            print(ajax_res_cnt)
            '''
            ajax_soup = BeautifulSoup(ajax_res_cnt, 'lxml')
            bibtex_url = ajax_soup.select('.gs_citi')[0]['href']
            bibtex_url = 'http://scholar.google.com' + bibtex_url
            res = request_with_proxy(bibtex_url)
            bibtex = res.content
            '''
        except Exception as e:
            print('ERROR:ParseHTML:bibtex')
            print(e)

        return bibtex

    def resource_type(self, sec):
        resource_type = None
        try:
            resource_type = sec.select('.gs_ggsS')[0].text.split(' ')[1][1:-1]
        except:
            pass
        return resource_type

    def resource_link(self, sec):
        resource_link = None
        try:
            resource_link = sec.select('.gs_md_wp > a')[0]['href']
        except:
            pass
        return resource_link

    def summary(self, sec):
        summary = None
        try:
            summary = sec.select('.gs_rs')[0].text
        except Exception as e:
            print("ERROR:ParseHTML:summary")
            print(e)
        return summary

    def google_id(self, sec):
        google_id = None
        try:
            google_id = sec.select('.gs_nph > a')[0]['onclick'].split('(')[-1].split(',')[0][1:-1]
        except Exception as e:
            print("ERROR:ParseHTML:google_id")
            print(e)
        return google_id

    # number in pages
    def index(self, sec):
        index = None
        try:
            index = sec.select('.gs_nph > a')[0]['onclick'].split('(')[-1].split(',')[1][1:-2]
        except Exception as e:
            print("ERROR:ParseHTML:index")
            print(e)
        return index

# instance object
#p = ParseHTML(url='https://scholar.google.com/scholar?hl=en&q=wenhua+yu&btnG=&as_sdt=1%2C5&as_sdtp=')
'''
p = ParseHTML(from_web=False)
for sec in p.sections():
    time.sleep(5)
    print('title',p.title(sec))
    print('year',p.year(sec))
    print('citations_count',p.citations_count(sec))
    print('link',p.link(sec))
    print('resource_type',p.resource_type(sec))
    print('resource_link',p.resource_link(sec))
    print('summary',p.summary(sec))
    print('google_id',p.google_id(sec))
    print('index',p.index(sec))
    #print('bibtex',p.bibtex(sec))
    print("===")
    print(p.citations_link(sec))
'''
