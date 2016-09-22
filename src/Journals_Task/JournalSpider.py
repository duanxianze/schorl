#coding:utf-8
"""
@file:      JournalSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-19 9:15
@description:
            The basic class of journal spider which contains public methods.
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from db_config import new_db_cursor

class JournalSpider:
    def __init__(self,JournalObj):
        self.JournalObj = JournalObj
        self.volume_links = []

    def mark_journal_ok(self):
        cur = new_db_cursor()
        cur.execute(
            'update journal set is_crawled_all_article = true\
             where sjr_id = {}'.format(self.JournalObj.sjr_id)
        )
        cur.close()

    def get_db_volume_item(self,volume_link):
        cur = new_db_cursor()
        cur.execute(
            "select is_crawled from journal_volume \
                where link = '{}' ".format(volume_link)
        )
        data = cur.fetchall()
        cur.close()
        return data

    def create_volume(self,volume_link):
        cur = new_db_cursor()
        '''
        try:
        '''
        cur.execute(
            "insert into journal_volume(link,journal_sjr_id,is_crawled)"
            "values(%s,%s,%s)",
            (volume_link,self.JournalObj.sjr_id,False)
        )
        #print('Save {} ok!'.format(volume_link))
        '''
        except Exception as e:
            print('[Error] in volume_link create:{} '.format(str(e)))
        '''
        cur.close()

    @property
    def saved_volumes_amount_of_journal(self):
        cur = new_db_cursor()
        cur.execute(
            'select count(*) from journal_volume \
              where journal_sjr_id={}'.format(self.JournalObj.sjr_id)
        )
        data = cur.fetchall()[0][0]
        cur.close()
        return data

    def mark_volume_ok(self,volume_link):
        cur = new_db_cursor()
        sql = "update journal_volume set is_crawled=true \
                where link='{}'".format(volume_link)
        #print(sql)
        cur.execute(sql)
        print('Mark volume {} ok!'.format(volume_link))

    def create_new_volumes(self):
        print('Init volume_links of {}...'.format(self.JournalObj.name))
        for volume_link in self.volume_links:
            self.create_volume(volume_link)
        if self.saved_volumes_amount_of_journal>10:
            cur = new_db_cursor()
            cur.execute(
                'update journal set volume_links_got=TRUE \
                  where sjr_id={}'.format(self.JournalObj.sjr_id)
            )
            cur.close()

    def get_unfinished_volume_links(self):
        if not self.JournalObj.volume_links_got:
            #第一次初始化
            self.create_new_volumes()
            return self.volume_links
        cur = new_db_cursor()
        cur.execute(
            'select link from journal_volume \
              where journal_sjr_id={} and is_crawled=FALSE'\
                .format(self.JournalObj.sjr_id)
        )
        data = cur.fetchall()
        cur.close()
        return list(map(
            lambda x:x[0],data
        ))

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    JournalObj=Journal()
    JournalObj.site_source = 'http://www.elsevier.com/wps/find/journaldescription.cws_home/505606/description#description'
    JournalObj.sjr_id = 1
    js = JournalSpider(JournalObj)
    js.mark_volume_ok('www.xxxx.com')
    #js.create_volume(volume_link='www.xxxx.com')