import os
import requests
requests.packages.urllib3.disable_warnings()
from multiprocessing.dummy import Pool as ThreadPool
import psycopg2

conn = psycopg2.connect(dbname="sf_development", user="gao", password="gaotongfei13")
cur = conn.cursor()

DOWNLOAD_FOLDER = "/home/gao/scholar_articles/download"

def download(url_googleid):
    try:
        url = url_googleid[0]
        google_id = url_googleid[1]
        download_folder_files = os.listdir(DOWNLOAD_FOLDER)
        if google_id not in download_folder_files:
            r = requests.get(url, verify=False)
            with open(os.path.join(DOWNLOAD_FOLDER, google_id), 'wb') as pdf_file:
                print('writing pdf file')
                pdf_file.write(r.content)
    except Exception as e:
        print(e)

pool = ThreadPool(8)
cur.execute("select resource_link, google_id from articles where id>=314060 and resource_link is not null and resource_type='PDF'")
url_googleids = cur.fetchall()
print(len(url_googleids))

results = pool.map(download, url_googleids)
pool.close()
pool.join()
