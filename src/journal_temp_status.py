#coding:utf-8
"""
@file:      journal_temp_status.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-04 15:20
@description:
            用于显示杂志社文章占比
"""
from db_config import conn,cur


cur.execute(
    'select journal_temp_info from articles where journal_temp_info is not null'
)

data_list=[]

journalObj = {
        'name':None,
        'cot':0
    }

def journal_in_data_list(journal_name):
    for journalObj in data_list:
        if journalObj['name'] == journal_name:
            return True
    return False


for item in cur.fetchall():
    journal_name = item[0]
    if not journal_in_data_list(journal_name):
        data_list.append(
            {
                'name': journal_name,
                'cot':  0
            }
        )
    #print(data_list)
    for journalObj in data_list:
        if journalObj['name'] == journal_name:
            journalObj['cot'] += 1

data_list = sorted(data_list,
        key=lambda x:x['cot'],
        reverse=False
    )

for data in data_list:
    print(data)


cur.execute(
    'select count(*) from articles where journal_temp_info is not null'
)

print('共{}'.format(cur.fetchall()[0][0]))