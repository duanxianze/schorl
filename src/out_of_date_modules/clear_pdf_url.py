#coding:utf-8
"""
@file:      clear_pdf_url
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-08 20:47
@description:
            resource_link未加unique约束，此脚本用于清理有重复的resource_link的item
            将其resource_link置为无效
"""

from db_config import cur

cur.execute(
    'select resource_link,count(resource_link)\
    from articles\
    where resource_link is not null\
    group by resource_link\
    order by count(resource_link ) desc limit 200'
)


for item in cur.fetchall():
    pdf_url = item[0]
    cot = item[1]
    if cot>1:
        print(item)
        cur.execute(
            "update articles set resource_link = null and is_downloaded = 0 \
            where resource_link = '{}'".format(pdf_url)
        )

print('done')