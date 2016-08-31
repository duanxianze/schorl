#coding:utf-8
"""
@file:      download.py
@python:    2.7
@editor:    PyCharm
@description:
            从db中检索出resource_link集,下载pdf
"""
import requests,psycopg2,os
requests.packages.urllib3.disable_warnings()
from multiprocessing.dummy import Pool as ThreadPool

conn = psycopg2.connect(
    host = '45.32.131.53',
    port = 5432,
    dbname = "sf_development",
    user = "gao",
    password = "gaotongfei13"
)
cur = conn.cursor()
conn.autocommit = True

DOWNLOAD_FOLDER = "./download"


class PdfDownloader:
    '''
        pdf下载器类，向远程数据库索取食物，喂给本地进程池下载
    '''
    def __init__(self,save_folder):
        #检查是否存在该文件夹，没有则创建
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        self.save_folder = save_folder
        self.download_folder_files = os.listdir(save_folder)

    def get_unfinished_items(self,length=1000):
        #从db中检索出未下载pdf的表项
        cur.execute(
            "select resource_link, google_id from articles where is_downloaded = 0 and resource_link is not null and resource_type='PDF' limit {}".format(length)
        )
        return cur.fetchall()

    def download(self,unfinished_item):
        #对于单条item的下载处理
        #print(unfinished_item)
        try:
            url = unfinished_item[0]
            google_id = unfinished_item[1]
            #若查询到该文件名不存在，即没有被下载，则执行下载
            save_name = google_id + '.pdf'
            if save_name not in self.download_folder_files:
                resp = requests.get(url, verify=False)
                with open(
                    os.path.join(self.save_folder, save_name), 'wb'
                ) as pdf_file:
                    pdf_file.write(resp.content)
                    self.download_folder_files.append(save_name)
            #下载完成后，在数据库中做记录：已下载
            cur.execute(
                "update articles set is_downloaded = 1 where google_id = %s",
                (google_id,)
            )
            print('Downloader:\n\t'+ save_name + ' wrote ok...')
        except Exception as e:
            cur.execute(
                "update articles set is_downloaded = -1 where google_id = %s",
                (google_id,)
            )
            print('Downloader:\n\t{}.pdf wrote error\n\t{}'.format(google_id,str(e)))
            #os.remove(path=save_name)

    def get_delta(self):
        print('Downloader:\n\tSearch file foler...')
        local_goole_ids = set(
            map(lambda x:x[:-4],self.download_folder_files)
        )
        print('Downloader:\n\tFind {} items in file folder'.format(len(local_goole_ids)))
        print('Downloader:\n\tSearch remote datebase unfinished items...')
        remote_google_ids = set(
            map(lambda x:x[1],self.get_unfinished_items(length=10000000))
        )
        print('Downloader:\n\tFind {} items in remote database'.format(len(remote_google_ids)))
        delta = local_goole_ids & remote_google_ids#求出交集
        print('Downloader:\n\tCaculate {} both-have items,mark them...'.format(len(delta)))
        return delta

    def mark_ok(self,google_id):
        cur.execute(
                    "update articles set is_downloaded = 1 where google_id = %s",
                    (google_id,)
                )
        print('Downloader:\n\t'+ google_id + ' wrote ok...')

    def initSync(self,pool):
        #初始化时检测增量，直接标记同步远程记录为1
        #本步骤建议在添加机器前使用，无需每次run都跑
        pool.map(self.mark_ok,self.get_delta())
        pool.close()
        pool.join()

    def run(self,thread_counts=8,init=False,shuffle=False):
        pool = ThreadPool(thread_counts)
        if init:
            self.initSync(pool)
        length = 1000
        print('Downloader:\n\tLoading {} items from remote database...'.format(length))
        unfinished_items = self.get_unfinished_items(length)
        #random.shuffle(unfinished_items)#打乱顺序
        pool.map(self.download, unfinished_items)
        #主循环，对于检索的结果列表中每个item都交给download函数执行
        pool.close()
        pool.join()


if __name__=='__main__':
    '''
    PdfDownloader(
        save_folder = DOWNLOAD_FOLDER,
    ).run(thread_counts=8)
    '''

    PdfDownloader(
        save_folder = DOWNLOAD_FOLDER,
    ).run(thread_counts=8,init=False,shuffle=False)
    #直接运行本文件，没有看门狗功能，请运行pdf_download_wacthdog.py,
    #进程运行一段时间，增量长时间为零，不能自动控制重启
    #由看门狗parent process调用本文件，作为sub process，控制并监测运行情况
