import os
import requests
from multiprocessing.dummy import Pool as ThreadPool
import psycopg2

conn = psycopg2.connect(dbname="sf_development", user="gao", password="gaotongfei13")
cur = conn.cursor()

DOWNLOAD_FOLDER = "/home/gao/scholar_articles/download"

def download(url_googleid):
    url = url_googleid[0]
    google_id = url_googleid[1]
    download_folder_files = os.listdir(DOWNLOAD_FOLDER)
    if google_id not in download_folder_files:
        r = requests.get(url)
        with open(os.path.join(DOWNLOAD_FOLDER, google_id), 'wb') as pdf_file:
            print('writing pdf file')
            pdf_file.write(r.content)
    else:
        print('pdf file already exists')

pool = ThreadPool(8)
cur.execute("select resource_link, google_id from articles where id>=314060 and resource_link is not null and resource_type='PDF'")
url_googleids = cur.fetchall()
print(len(url_googleids))

results = pool.map(download, url_googleids[:8])
pool.close()
pool.join()
