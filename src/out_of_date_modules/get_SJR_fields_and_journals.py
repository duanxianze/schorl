#coding:utf-8
"""
@file:      get_SJR_fields_and_journals
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-12 22:04
@description:
            得到SJR排名网站上每个领域和专业表
"""
import time
from selenium import webdriver
from src.db_config import cur

'''
#未得到数据库sjr_area表前的代码
driver = webdriver.Chrome()

driver.get('http://www.scimagojr.com/journalrank.php')

time.sleep(3)

driver.find_element_by_xpath('//*[@id="rankingcontrols"]/div[1]').click()

rankingcontrols = driver.find_element_by_id('rankingcontrols')
area_and_category_field = rankingcontrols.\
                            find_elements_by_tag_name('ul')[:2]

hrefs = []
for area_li in area_and_category_field[0]\
                .find_elements_by_tag_name('li'):
    a = area_li.find_element_by_tag_name('a')
    area_name = a.text
    area_href = a.get_attribute('href')
    hrefs.append(area_href)
    area_id = area_href.split('?')[-1].split('=')[-1]
    try:
        area_id = int(area_id)
    except:
        continue
    print(area_name,area_href,area_id)
    cur.execute(
        'insert into sjr_area(name,sjr_id)'
        'values(%s,%s)',
        (area_name,area_id)
    )

hrefs = hrefs[1:]
'''

cur.execute(
    'select name,sjr_id,id from sjr_area'
)
data = cur.fetchall()
print(data)

driver = webdriver.Chrome()


'''以下是未得到category表前的执行代码，之后执行会触发sjr_id的unique约束'''
for item in data:
    #print(item)
    name = item[0]
    sjr_id = item[1]
    area_db_id = item[2]
    print(sjr_id,area_db_id,name)
    href = 'http://www.scimagojr.com/journalrank.php?area={}'.format(sjr_id)
    driver.get(href)
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="rankingcontrols"]/div[2]').click()
    rankingcontrols = driver.find_element_by_id('rankingcontrols')
    area_and_category_field = rankingcontrols.\
                            find_elements_by_tag_name('ul')[:2]
    for category_li in area_and_category_field[1].find_elements_by_tag_name('li'):
        a = category_li.find_element_by_tag_name('a')
        category_name = a.text
        category_href = a.get_attribute('href')
        category_id = int(category_href.split('=')[-1])
        if category_id%100 == 0:
            #是area_id
            continue
        print(category_name,category_href,category_id)
        cur.execute(
            'insert into sjr_category(name,area_id,sjr_id)'
            'values(%s,%s,%s)',
            (category_name,area_db_id,category_id)
        )

