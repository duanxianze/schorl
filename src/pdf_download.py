#coding:utf-8
"""
@file:      download.py
@python:    2.7
@editor:    PyCharm
@description:
            从db中检索出resource_link集,下载pdf
"""
import requests,os,random
requests.packages.urllib3.disable_warnings()
from multiprocessing.dummy import Pool as ThreadPool
from db_config import conn,cur

if os.name is 'nt':
    DOWNLOAD_FOLDER = "F:/scholar_articles/src/download/"
else:
    DOWNLOAD_FOLDER = "~/scholar_articles/src/download/"

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

    def get_max_unfinished_item_id(self):
        cur.execute(
            "select max(id) from articles where is_downloaded = 0 and resource_link is not null and resource_type='PDF'"
        )
        return cur.fetchall()[0][0]

    def get_unfinished_items(self,left=None,length=1000):
        #从db中检索出未下载pdf的表项
        max_id = self.get_max_unfinished_item_id()
        left = random.randint(1,max_id-length)
        right = left + length
        cur.execute(
            "select resource_link, google_id from articles where is_downloaded = 0 and resource_link is not null and resource_type='PDF' and id > {} and id < {}".format(left,right)
        )
        data = cur.fetchall()
        print('PdfDownloader:\n\tGot {} items in range [{},{}]'.format(len(data),left,right))
        return data

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
                    file_kb = os.path.getsize(self.save_folder+save_name)*1.0 / 1024
                    if file_kb > 3:
                        self.download_folder_files.append(save_name)
                        print('Downloader:\n\t'+ save_name + '( {} Kb ) wrote ok...'.format(file_kb))
                    else:
                        raise Exception('File size = {}k < 3k'.format(file_kb))
            #下载完成后，在数据库中做记录：已下载
            self.mark(google_id,ok=True)
        except Exception as e:
            self.mark(google_id,ok=False,err=e)

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

    def mark(self,google_id,ok=True,err=None):
        if ok:
            cur.execute(
                        "update articles set is_downloaded = 1 where google_id = %s",
                        (google_id,)
                    )
            print('Databse:\n\t'+ google_id + ' update ok...')
        else:
            cur.execute(
                "update articles set is_downloaded = -1 where google_id = %s",
                (google_id,)
            )
            print('Downloader:\n\t{}.pdf wrote error\n\t{}'.format(google_id,str(err)))


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
        while True:
            print('Downloader:\n\tLoading items from remote database...'.format(length))
            unfinished_items = self.get_unfinished_items(length)
            if len(unfinished_items)>0:
                break
        #random.shuffle(unfinished_items)#打乱顺序
        result = pool.map(self.download, unfinished_items)
        print('pool_result:',result)
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
    ).run(thread_counts=32,init=False,shuffle=False)
    #直接运行本文件，没有看门狗功能，请运行pdf_download_wacthdog.py,
    #进程运行一段时间，增量长时间为零，不能自动控制重启
    #由看门狗parent process调用本文件，作为sub process，控制并监测运行情况
