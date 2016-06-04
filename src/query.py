import psycopg2
import re
from bs4 import BeautifulSoup
from request_with_proxy import request_with_proxy
from math import ceil
from parse_html import ParseHTML

DB_NAME = "sf_development"
USER = "gao"
PASSWORD = "gaotongfei13"
conn = psycopg2.connect("dbname={0} user={1} password={2}".format(DB_NAME, USER, PASSWORD))
conn.autocommit = True
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
            pass
        return p 


    def page_urls(self):
        #pages = self.page()
        pages = 10
        
        urls = ['https://scholar.google.com/scholar?start={0}&q={1}&hl=en&as_sdt=0,5'.format(p*10-10, self.full_name) for p in range(1, pages+1)]

        return urls 


#cur.execute("select id, first_name, middle_name, last_name from scholars where is_added = 0")
cur.execute("select id, first_name, middle_name, last_name from scholars where is_added = 0")
names =  [n for n in cur.fetchall()]

for name in names:
    id = name[0]
    query = QueryDB(name[1:])
    print(id)
    print(name)
    page_urls = query.page_urls()
    for p in page_urls:
        print("for p in page")
        print(p)
        parse_html = ParseHTML(url=p)
        print(parse_html)
        print(parse_html.sections())
        for sec in parse_html.sections():
            print("for sec in parse_html.secions()")
            print(sec)
            try:
                print("try...")
                title = parse_html.title(sec)
                year = parse_html.year(sec)
                citations_count = parse_html.citations_count(sec)
                link = parse_html.link(sec)
                resource_type = parse_html.resource_type(sec)
                resource_link = parse_html.resource_link(sec)
                summary = parse_html.summary(sec)
                google_id = parse_html.google_id(sec)
                #bibtex = parse_html.bibtex(sec)
                #print("({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})".format(title, year, citations_count, link, resource_type, resource_link, summary, google_id))
                #print("google_id: {0}".format(google_id))
                cur.execute("insert into articles (title, year, citations_count, link, resource_type, resource_link, summary, google_id) "
                        "values (%s, %s, %s, %s, %s, %s, %s, %s) on conflict do nothing", (title, year, citations_count, link, resource_type, resource_link, summary, google_id))
            except Exception as e:
                print(e)

    cur.execute("update scholars set is_added = 1 where id = (%s)", (id,))

cur.close()
conn.close()
