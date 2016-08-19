#coding:utf-8
"""
@file:      download.py
@python:    3.3
@editor:    PyCharm
@description:
            从db中检索出resource_link集,下载pdf
"""
import os,time
import requests
requests.packages.urllib3.disable_warnings()
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process
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
        #检查是否存在该文件夹，没有则创建
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        self.save_folder = save_folder
        self.statusMonitor = StatusMonitor()

    def download(self,unfinished_item):
        #对于单条item的下载处理
        #print(unfinished_item)
        try:
            url = unfinished_item[0]
            google_id = unfinished_item[1]
            #列出下载目录的文件名列表
            download_folder_files = os.listdir(self.save_folder)
            #若查询到该文件名不存在，即没有被下载，则执行下载
            save_name = google_id + '.pdf'
            if save_name not in download_folder_files:
                resp = requests.get(url, verify=False)
                with open(
                    os.path.join(self.save_folder, save_name), 'wb'
                ) as pdf_file:
                    pdf_file.write(resp.content)
                    print(save_name + ' wrote ok...')
            #下载完成后，在数据库中做记录：已下载
            cur.execute(
                "update articles set is_downloaded = 1 where google_id = %s",
                (google_id,)
            )
        except Exception as e:
            print('download( google_id = "{}" ) ERROR:\n\t{}'.format(google_id,str(e)))

    def run_monitor(self):
        while True:
            print(
                'pdf_files:',
                self.statusMonitor.counts_of_pdf_files,
            )
            time.sleep(10)

    def run(self):
        print('length = ',len(self.statusMonitor.unfinished_items))
        pool = ThreadPool(5)
        pool.map(self.download, self.statusMonitor.unfinished_items)
        #主循环，对于检索的结果列表中每个item都交给download函数执行
        Process(
            target=self.run_monitor(),
            args=(1,)
        ).start()
        pool.close()
        pool.join()


class StatusMonitor:
    '''
        关于pdf下载的数据监视器类
    '''
    def __init__(self):
        pass

    @property
    def unfinished_items(self,extend_cursor=None):
        #db中未下载的条目集
        if extend_cursor:
            cursor = extend_cursor
        else:
            cursor = cur
        #从db中检索出未下载pdf的表项
        cursor.execute(
            "select resource_link, google_id from articles where is_downloaded = 0 and resource_link is not null and resource_type='PDF'"
        )
        return cur.fetchall()

    @property
    def counts_of_finished_db_item(self,extend_cursor=None):
        #db显示已下载项的数量
        if extend_cursor:
            cursor = extend_cursor
        else:
            cursor = cur
        cursor.execute(
            "select count(id) from articles where is_downloaded = 1"
        )
        return cur.fetchall()

    @property
    def counts_of_unfinished_db_item(self,extend_cursor=None):
        #db显示未下载项的数量
        if extend_cursor:
            cursor = extend_cursor
        else:
            cursor = cur
        cursor.execute(
            "select count(id) from articles where is_downloaded = 0"
        )
        return cur.fetchall()

    @property
    def counts_of_pdf_files(self,extend_folder=None):
        #下载文件夹中pdf文件的数量
        if extend_folder:
            folder = extend_folder
        else:
            folder = DOWNLOAD_FOLDER
        return len(os.listdir(folder))


if __name__=='__main__':
    PdfDownloader(DOWNLOAD_FOLDER).run()

