# coding=utf8
from selenium import webdriver
import time
from pyvirtualdisplay import Display
import psycopg2
import bibtexparser

display = Display(visible=0, size=(800, 600))
display.start()

profile = webdriver.FirefoxProfile()
profile.set_preference('network.proxy.type', 1)
profile.set_preference('network.proxy.socks', '127.0.0.1')
profile.set_preference('network.proxy.socks_port', 1107)
profile.set_preference('permissions.default.image', 2)
profile.set_preference('browser.link.open_newwindow', 1)


browser = webdriver.Firefox(profile)

conn = psycopg2.connect(dbname="sf_development", user="gao", password="gaotongfei13")
conn.autocommit = True
cur = conn.cursor()

cur.execute("select id, google_id from articles where id > 314073 and bibtex is null")
result_sets = cur.fetchall()
print("{} tasks running".format(len(result_sets)))
for id, google_id in result_sets:
    try:
        bibtex = None
        url = 'https://scholar.google.com/scholar?q=info:{}:scholar.google.com/&output=cite&scirp=0&hl=en'.format(google_id)

        print("id: {0} google_id: {1}".format(id, google_id))
        print("url: {}".format(url))

        browser.get(url)
        #with open('a.html', 'w') as f:
        #f.write(browser.page_source)
        bibtex_url = browser.find_element_by_css_selector("#gs_citi > a").get_attribute('href')
        # 访问bibtex 链接
        browser.get(bibtex_url)
        bibtex = browser.page_source
        bib = bibtexparser.loads(bibtex)
        if bib:
            entries = bib.entries
            if entries:
                # bibtex 是有效的, 写入数据库
                cur.execute("update articles set bibtex = %s where id = %s", (bibtex, id))
            else:
                # bibtex 无效
                pass

        time.sleep(20)
    except Exception as e:
        time.sleep(20)
        print(e)
        
browser.quit()
display.stop()
