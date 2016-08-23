#coding:utf-8
"""
@file:      download.py
@python:    2.7
@editor:    PyCharm
@description:
            从db中检索出resource_link集,下载pdf
"""
import random,requests,psycopg2,os
requests.packages.urllib3.disable_warnings()
from multiprocessing.dummy import Pool as ThreadPool

conn = psycopg2.connect(
    dbname="sf_development",
    user="postgres",
    password=""
)
cur = conn.cursor()

DOWNLOAD_FOLDER = "./download"


class PdfDownloader:
    '''
        pdf下载器类
    '''
    def __init__(self,save_folder):
        #检查是否存在该文件夹，没有则创建
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        self.save_folder = save_folder

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
                    print('Downloader:\n\t'+ save_name + ' wrote ok...')
            #下载完成后，在数据库中做记录：已下载
            cur.execute(
                "update articles set is_downloaded = 1 where google_id = %s",
                (google_id,)
            )
            conn.commit()
        except Exception as e:
            cur.execute(
                "update articles set is_downloaded = -1 where google_id = %s",
                (google_id,)
            )
            conn.commit()
            print('Downloader:\n\tdownload( google_id = "{}" ) ERROR:\n\t{}'.format(google_id,str(e)))

    def run(self,thread_counts=8):
        pool = ThreadPool(thread_counts)
        unfinished_items = self.unfinished_items
        random.shuffle(unfinished_items)#打乱顺序
        pool.map(self.download, unfinished_items)
        #主循环，对于检索的结果列表中每个item都交给download函数执行
        pool.close()
        pool.join()


if __name__=='__main__':
    PdfDownloader(
        save_folder = DOWNLOAD_FOLDER,
    ).run(thread_counts=10)
    #直接运行本文件，没有看门狗功能，请运行pdf_download_wacthdog.py,
    #进程运行一段时间，增量长时间为零，不能自动控制重启
    #由看门狗parent process调用本文件，作为sub process，控制并监测运行情况
