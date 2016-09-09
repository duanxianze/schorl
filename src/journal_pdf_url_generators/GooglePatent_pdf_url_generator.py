#coding:utf-8
"""
@file:      GooglePatent_pdf_url_generator.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-09 21:38
@description:
            谷歌专利的pdf下载器
"""
from db_config import cur
from pdf_download import PdfDownloader,DOWNLOAD_FOLDER
from multiprocessing.dummy import Pool as ThreadPool

class GooglePatent_PDF_Downloader:
    def __init__(self):
        pass

    def get_unfinished_items(self,limit=100000000):
        cur.execute(
            "select link,google_id from articles where journal_temp_info like '%Patents%' and resource_link is null limit {}".format(limit)
        )
        data = cur.fetchall()
        print('Loading {} items'.format(len(data)))
        return data

    def mark(self,pdf_url,google_id):
        cur.execute(
            "update articles set resource_link = '{}' where google_id = '{}'".format(pdf_url,google_id)
        )
        print('{} ok'.format(google_id))

    def download(self,item):
        google_id = item[1]
        patent_id = item[0].split('/')[-1]
        pdf_url = 'https://patentimages.storage.googleapis.com/pdfs/{}.pdf'.format(patent_id)
        print(google_id,patent_id)
        if PdfDownloader(save_folder=DOWNLOAD_FOLDER).download(
            unfinished_item = (pdf_url,google_id),
            need_mark_err = False
        ):
            self.mark(pdf_url,google_id)

    def run(self):
        pool = ThreadPool(16)
        pool.map(self.download,self.get_unfinished_items())
        pool.close()
        pool.join()

if __name__=="__main__":
    GooglePatent_PDF_Downloader().run()
