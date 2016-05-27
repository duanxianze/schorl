import psycopg2
import re
from bs4 import BeautifulSoup
from request_with_proxy import request_with_proxy
from math import ceil

DB_NAME = "sf_development"
USER = "gao"
PASSWORD = "gaotongfei13"
conn = psycopg2.connect("dbname={0} user={1} password={2}".format(DB_NAME, USER, PASSWORD))
cur = conn.cursor()

class QueryDB:
    def __init__(self,name):
        self.name = name
        self.url = []
        if self.name[1].strip()=='':
            self.full_name = self.name[0].strip() + ' ' + self.name[2].strip()
            self.start_url = 'https://scholar.google.com/scholar?start=0&q='+self.full_name+'&hl=en&as_sdt=0,5'
        else:
            self.full_name = self.name[0].strip() + ' ' + self.name[1].strip() + ' ' + self.name[2].strip()
            self.start_url = 'https://scholar.google.com/scholar?start=0&q='+self.full_name+'&hl=en&as_sdt=0,5'


    def page(self):
        p = 10
        r = request_with_proxy(self.start_url)
        if r:
            soup = BeautifulSoup(r.text, "lxml")
            about = soup.select("#gs_ab_md")
            if about:
                result = about[0].text
                result_num = re.findall("About\s+([\w\,]+)\s+results", result)
                if result_num:
                    result_num = result_num[0].replace(",", "")
                    p = int(ceil(int(result_num)/float(10)))
        else:
            print(r.status_code)
        return p 


    def page_url(self):
        """
        page 大于100，按照100处理，因为google scholar最多只能查询到100页
        """
        pages = self.page()
        if pages > 100:
            pages = 100
        
        urls = ['https://scholar.google.com/scholar?start={0}&q={1}&hl=en&as_sdt=0,5'.format(p*10-10, self.full_name) for p in range(1, pages+1)]

        return urls 


cur.execute("select first_name, middle_name, last_name from scholars where id >=1000")
names =  [n for n in cur.fetchall()]

for name in names:
    query = QueryDB(name)
    print(name)
    print(query.start_url)
    print(query.page_url())
    #print(query.page)

