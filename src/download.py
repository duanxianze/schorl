#coding:utf-8
'''
    dowmload.py 用于下载pdf文件
'''
import os
import requests
requests.packages.urllib3.disable_warnings()
from multiprocessing.dummy import Pool as ThreadPool
import psycopg2

'''连接数据库'''
conn = psycopg2.connect(dbname="sf_development", user="gao", password="gaotongfei13")
cur = conn.cursor()

'''设置pdf下载保存路径'''
DOWNLOAD_FOLDER = "./download"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

'''
download函数：
    传入由pdf的url以及google_id组成的元组
'''
def download(url_googleid):
    try:
        url = url_googleid[0]
        google_id = url_googleid[1]
        '''列出下载目录的文件名列表'''
        download_folder_files = os.listdir(DOWNLOAD_FOLDER)
        '''若查询到该文件名不存在，即没有被下载，则执行下载'''
        if google_id not in download_folder_files:
            r = requests.get(url, verify=False)
            with open(os.path.join(DOWNLOAD_FOLDER, google_id), 'wb') as pdf_file:
                print('writing pdf file')
                pdf_file.write(r.content)
        '''下载完成后，在数据库中做记录：已下载'''
        cur.execute("update articles set is_downloaded = 1 where google_id = %s", (google_id,))
    except Exception as e:
        print(e)


'''为主任务分配线程'''
pool = ThreadPool(8)
'''从db中检索出未下载pdf的表项'''
cur.execute("select resource_link, google_id from articles where is_downloaded = 0 and resource_link is not null and resource_type='PDF'")
url_googleids = cur.fetchall()
print(len(url_googleids))
'''主循环，对于检索的结果列表中每个项目都交给download函数执行'''
results = pool.map(download, url_googleids)
pool.close()
pool.join()
