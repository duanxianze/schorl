from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
import requests
requests.packages.urllib3.disable_warnings()
from random import randint
import socks
import socket

class ParseHTML:
    def __init__(self, use_proxy=False):
        with open('scholar_articles.htm', 'rb') as f:
            self.html = f.read()

        self.soup = BeautifulSoup(self.html, 'lxml')
        self.html_text = self.soup.text
        self.rand_port = lambda x, y: randint(x, y)
        self.use_proxy = use_proxy
        self.ua = UserAgent()
        
    def sections(self):
        sections = self.soup.select('.gs_r')
        return sections

    def title(self, sec):
        title = sec.select('.gs_rt > a')[0].text
        return title

    def year(self, sec):
        year = sec.select('.gs_a')[0].text.split('-')[-2].split(',')[-1][1:-1]
        return year

    def citations_count(self, sec):
        citations_count = sec.select('.gs_fl > a')[0].text[9:]
        citations_count = int(citations_count)
        return citations_count

    def link(self, sec):
        link = sec.select('.gs_rt > a')[0]['href']
        return link

    def request_with_proxy(self, url, timeout=10):
        headers = {'User-Agent': self.ua.random}
        print(headers)
        print(requests.get('https://api.ipify.org').text)
        r = None
        proxy_port = self.rand_port(9053, 9113)
        socks.set_default_proxy(socks.SOCKS5, "localhost", proxy_port)
        socket.socket = socks.socksocket
        r = requests.get(url, headers=headers)
        return r


    # need to config proxy in terminal
    def bibtex(self, sec):
        proxies = None
        bibtex = None
        ajax_url = 'https://scholar.google.co.jp/scholar?q=info:' + self.google_id(sec) +':scholar.google.com/&output=cite&scirp='+ self.index(sec) +'&hl=en'
        ajax_url = 'http' + ajax_url[5:]
        try:
            ajax_res = self.request_with_proxy(ajax_url)
            print(ajax_res)
            ajax_res_cnt = ajax_res.content
            #print('ajax_res_cnt:',ajax_res_cnt)
            ajax_soup = BeautifulSoup(ajax_res_cnt, 'lxml')
            bibtex_url = ajax_soup.select('.gs_citi')[0]['href']
            bibtex_url = 'http://scholar.google.com' + bibtex_url
            res = self.request_with_proxy(bibtex_url)
            bibtex = res.content
        except Exception as e:
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
        summary = sec.select('.gs_rs')[0].text
        return summary

    def google_id(self, sec):
        google_id = sec.select('.gs_nph > a')[0]['onclick'].split('(')[-1].split(',')[0][1:-1]
        return google_id

    # number in pages
    def index(self, sec):
        index = sec.select('.gs_nph > a')[0]['onclick'].split('(')[-1].split(',')[1][1:-2]
        return index

# instance object
p = ParseHTML(use_proxy=True)
for sec in p.sections():
    time.sleep(5)
    #print('title',p.title(sec))
    #print('year',p.year(sec))
    #print('citations_count',p.citations_count(sec))
    #print('link',p.link(sec))
    #print('resource_type',p.resource_type(sec))
    #print('resource_link',p.resource_link(sec))
    #print('summary',p.summary(sec))
    #print('google_id',p.google_id(sec))
    #print('index',p.index(sec))
    print('bibtex',p.bibtex(sec))
    print("===")
