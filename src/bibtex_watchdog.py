#coding:utf-8
"""
@file:      bibtex_watchdog.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-26 16:23
@description:
            用于监测bibtex.py的工作情况
"""

from WatchDog import WatchDog
from bibtex import *


class Bibtex_Spider_WatchDog(WatchDog):
    def __init__(self,cmd_line,task_proc_cmd_line,pid=None):
        WatchDog.__init__(cmd_line,task_proc_cmd_line,pid)

    @property
    def bibtex_not_null_article_amount(self):
        cur.execute(
            'select count(*) from articles where where id > 314083 and bibtex is not null'
        )
        return int(cur.fetchall()[0][0])

    def run(self):
        while(1):
            local_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            print('WatchDog:\n\t{},\t{},\t{}'.format(
                        self.bibtex_not_null_article_amount,
                        self.task_proc_status,
                        time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                    )
                )
            if self.task_proc_status is 'dead':
                self.restart_task_proc()
            time.sleep(10)


if __name__=="__main__":
    Bibtex_Spider_WatchDog(
        cmd_line = ['python','bibtex_watchdog.py'],
        task_proc_cmd_line = ['python','bibtex.py']
    ).run()