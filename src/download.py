#coding:utf-8
'''
    dowmload.py 用于下载pdf文件
'''
import os
import requests
requests.packages.urllib3.disable_warnings()
from multiprocessing.dummy import Pool as ThreadPool
import psycopg2

'''设置数据库连接'''
conn = psycopg2.connect(
    dbname="sf_development",
    user="postgres",
    password=""
)
cur = conn.cursor()

'''设置pdf下载保存路径'''
DOWNLOAD_FOLDER = "./download"


class PdfDownloader:
    def __init__(self,save_folder):
        ''''''
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        self.save_folder = save_folder

    @property
    def unfinished_items(self):
        '''从db中检索出未下载pdf的表项'''
        cur.execute(
            "select resource_link, google_id from articles where is_downloaded = 0 and resource_link is not null and resource_type='PDF'"
        )
        return cur.fetchall()

    def download(self,unfinished_item):
        '''对于单条item的下载处理'''
        try:
            url = unfinished_item[0]
            google_id = unfinished_item[1]
            '''列出下载目录的文件名列表'''
            download_folder_files = os.listdir(self.save_folder)
            '''若查询到该文件名不存在，即没有被下载，则执行下载'''
            if google_id+'.pdf' not in download_folder_files:
                r = requests.get(url, verify=False)
                with open(os.path.join(self.save_folder, google_id+'.pdf'), 'wb') as pdf_file:
                    print(google_id+'.pdf writing...')
                    pdf_file.write(r.content)
            '''下载完成后，在数据库中做记录：已下载'''
            cur.execute("update articles set is_downloaded = 1 where google_id = %s", (google_id,))
        except Exception as e:
            print('download() ERROR:',str(e))

    def run(self):
        print('length = ',len(self.unfinished_items))
        pool = ThreadPool(8)
        results = pool.map(self.download, self.unfinished_items)
        '''主循环，对于检索的结果列表中每个item都交给download函数执行'''
        pool.close()
        pool.join()


if __name__=='__main__':
    PdfDownloader(DOWNLOAD_FOLDER).run()

