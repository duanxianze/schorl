#coding:utf-8
'''
    task.py 由学者姓名列表出发，做爬取分析，是本爬虫任务核心
'''
import psycopg2
import re
from bs4 import BeautifulSoup
from request_with_proxy import request_with_proxy
from math import ceil
from parse_html import ParseHTML

'''设置数据库'''
DB_NAME = "sf_development"
USER = "gao"
PASSWORD = "gaotongfei13"
'''连接数据库'''
conn = psycopg2.connect("dbname={0} user={1} password={2}".format(DB_NAME, USER, PASSWORD))
conn.autocommit = True  #设置数据库自动提交
cur = conn.cursor()

class ScholarSearch:
    def __init__(self,name):
        '''
            传入参数：
                name:       从学者表中检索出的学者名字元组，包含first_name, middle_name, last_name
            包含属性：
                self.name:        学者姓名元组
                self.full_name :  学者完整姓名，将上方姓名元组整合得到
                self.start_url :  搜索学者姓名，其结果的起始url
        '''
        self.name = name
        if self.name[1].strip()=='':
            '''
                对于full_name的运算，若middle_name不存在，需要区分对待
            '''
            self.full_name = self.name[0].strip() + ' ' + self.name[2].strip()
            self.start_url = 'https://scholar.google.com/scholar?start=0&q='+self.full_name+'&hl=en&as_sdt=0,5'
        else:
            self.full_name = self.name[0].strip() + ' ' + self.name[1].strip() + ' ' + self.name[2].strip()
            self.start_url = 'https://scholar.google.com/scholar?start=0&q='+self.full_name+'&hl=en&as_sdt=0,5'


    def page(self):
        '''
            访问通过start_url，解析页面元素，得到文章数量
            算出该学者搜索结果的页数，作为返回值
        '''
        p = 10
        r = request_with_proxy(self.start_url)
        if r:
            '''如果有返回结果'''
            soup = BeautifulSoup(r.text, "lxml")
            about = soup.select("#gs_ab_md")
            if about:
                result = about[0].text
                result_num = re.findall("About\s+([\w\,]+)\s+results", result)
                if result_num:
                    '''找到文章数，算出总页数'''
                    result_num = result_num[0].replace(",", "")
                    p = int(ceil(int(result_num)/float(10)))#ceil取整
        return p


    def page_urls(self):
        '''
            得到搜索结果页数，
            并生成每页url的集合，作为返回值
        '''
        pages = self.page()
        if pages>10:
            pages = 10
        '''10页以后意义不大，故大于10页取10页爬取'''
        urls = ['https://scholar.google.com/scholar?start={0}&q={1}&hl=en&as_sdt=0,5'.format(p*10-10, self.full_name) for p in range(1, pages+1)]
        return urls


'''从scholar表中检索出学者名列表'''
cur.execute("select id, first_name, middle_name, last_name from scholars where is_added = 0")
#cur.execute("select id, first_name, middle_name, last_name from scholars where id = (select max(id)-1 from scholars)")
names =  [n for n in cur.fetchall()]

'''对于每一个学者'''
for name in names:
    try:
        id = name[0]
        query = ScholarSearch(name[1:])
        print(id)
        print(name)
        '''从实例化类中得到关于该学者的搜索结果的所有页面url'''
        page_urls = query.page_urls()
        for p in page_urls:
            '''对于每一页，都交给ParseHTML模型解析'''
            print("for p in page")
            print(p)
            parse_html = ParseHTML(url=p)
            print(parse_html)
            print(parse_html.sections())
            for sec in parse_html.sections():
                '''对于每一篇文章，分布提取元素'''
                print("for sec in parse_html.secions()")
                print(sec)
                try:
                    print("try...")
                    title = parse_html.title(sec)
                    year = parse_html.year(sec)
                    citations_count = parse_html.citations_count(sec)
                    citations_link = parse_html.citations_link(sec)
                    link = parse_html.link(sec)
                    resource_type = parse_html.resource_type(sec)
                    resource_link = parse_html.resource_link(sec)
                    summary = parse_html.summary(sec)
                    google_id = parse_html.google_id(sec)
                    #bibtex = parse_html.bibtex(sec)
                    print("({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})".format(title, year, citations_count, link, resource_type, resource_link, summary, google_id))
                    #print("google_id: {0}".format(google_id))
                    '''各项写入文章表'''
                    cur.execute("insert into articles (title, year, citations_count, citations_link, link, resource_type, resource_link, summary, google_id) "
                            "values (%s, %s, %s, %s, %s, %s, %s, %s, %s) on conflict do nothing", (title, year, citations_count, citations_link, link, resource_type, resource_link, summary, google_id))
                except Exception as e:
                    print(e)
        '''更新数据库中学者的记录is_added = 1，表示已经爬取过他的文章集合'''
        cur.execute("update scholars set is_added = 1 where id = (%s)", (id,))
    except Exception as e:
        print(e)

'''与数据库连接断开'''
cur.close()
conn.close()
