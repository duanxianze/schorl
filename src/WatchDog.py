#coding:utf-8
"""
@file:      WatchDog.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-19 14:33
@description:
            --
"""
from emailClass import Email
import psutil,os


def get_existed_proc(cmd_line):
    #cmd_line is like:  ['python','amount_status.py']
    for proc in psutil.process_iter():
        try:
            if proc.cmdline is cmd_line:
                return proc  # return if found one
        except psutil.AccessDenied:
            pass
        except psutil.NoSuchProcess:
            pass
    return None


class WatchDog:
    '''
        对于每个process(对应于每个任务)的监视管理器
        如果需要定制，可做父类继承
    '''
    def __init__(self,proc_cmd_line,pid=None):
        self.proc_cmd_line = proc_cmd_line
        self.proc = get_existed_proc(proc_cmd_line)
        if pid:
            self.proc = psutil.Process(pid)
        if not self.proc:
            self.create_proc()
            self.proc = get_existed_proc(proc_cmd_line)

    def send_mail(self,admin_address,subject):
        emailAI = Email(
            receiver = admin_address,
            sender   = 'luyangaini@vip.qq.com',
            subject  = subject,
            content  = 'rt',
        )
        emailAI.conn_server(
            host='smtp.qq.com',
            port = 587
        )
        emailAI.login(
            username='luyangaini@vip.qq.com',
            password='ptuevbbulatcbcfh'
        )
        emailAI.send()
        emailAI.close()

    def close_proc(self):
        cmd = 'kill -9 ' + str(self.proc.pid)
        os.system(cmd)
        print('execute cmd: " %s " ...'.format(cmd))

    def create_proc(self):
        common_cmd = ' '.join(self.proc_cmd_line)
        nohup_cmd = 'nohup ' + common_cmd + ' & '
        os.system(nohup_cmd)
        print('execute cmd: " %s " ...'.format(nohup_cmd))

    def restart(self):
        self.close_proc()
        self.create_proc()
        self.proc = get_existed_proc(self.proc_cmd_line)
        print('Restart ok! The new pid is: ' + self.proc.pid)

    @property
    def proc_status(self):
        return self.proc.status()

    def run(self):
        pass
        '''
        maybe like that:
            while(1):
                if self.proc_status is 'sleeping':
                    self.send_mail('fuck')
                time.sleep(timeout)
        '''