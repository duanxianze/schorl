#coding:utf-8
"""
@file:      PublishersGenerator.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-16 23:07
@description:
            由journal表中数据,填充publisher表
"""
def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result = a[x-1] + result
            x -= 1
            y -= 1
    return result

from src.db_config import new_db_cursor

cur = new_db_cursor()

#找出杂志社排名数量前300的出版商，工作重点在前50，不少巨无霸出版社
cur.execute(
    'SELECT publisher FROM journal \
      GROUP BY publisher ORDER BY count(*) DESC limit 300'
)
publishers = list(map(lambda x:x[0],cur.fetchall()))

print(publishers)

for publisher_name in publishers:
    print(publisher_name)
    cur.execute(
        "SELECT site_source FROM journal WHERE publisher = '{}' limit 10"\
            .format(publisher_name)
    )
    site_source_set = list(map(lambda x:x[0],cur.fetchall()))
    #print(site_source_set,type(site_source_set),len(site_source_set))
    sample_url = None
    for source in site_source_set:
        if source:
            sample_url = source
            break
    if not sample_url:
        print('Sample Url is None')
        continue
    try:
        cur.execute(
            'insert into publisher(name,sample_url)'
            'VALUES(%s,%s)',
            (publisher_name,sample_url)
        )
    except Exception as e:
        print(str(e))
    print('{} save ok'.format(publisher_name))
    print('-------------')