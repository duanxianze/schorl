#coding:utf-8
"""
@file:      WatchDog.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    2.7
@editor:    PyCharm
@create:    2016-08-19 14:33
@description:
            The basic class of process monitor of one specific task.
"""
from emailClass import Email
import psutil,os,subprocess


def get_existed_proc(cmd_line=None,pname=None):
    #cmd_line is like:  ['python','amount_status.py']
    for proc in psutil.process_iter():
        try:
            if proc.cmdline() == cmd_line:
                return proc  # return if found one
            if pname is not None and proc.name().lower() == pname.lower():
                return proc
        except psutil.AccessDenied:
            pass
        except psutil.NoSuchProcess:
            pass
    return None


def get_prev_pids(cmd_line=None,pname=None):
    #cmd_line is like:  ['python','amount_status.py']
    print('cmd_line',cmd_line)
    prev_pids = []
    for proc in psutil.process_iter():
        try:
            if proc.cmdline() == cmd_line:
                prev_pids.append(proc.pid)
            if pname is not None and proc.name().lower() == pname.lower():
                prev_pids.append(proc.pid)
        except psutil.AccessDenied:
            pass
        except psutil.NoSuchProcess:
            pass
    return prev_pids[:-1]


class WatchDog:
    '''
        对于每个process(对应于每个任务)的监视管理器
        如果需要定制，可做父类继承
    '''
    def __init__(self,self_cmd_line,proc_cmd_line,pid=None):
        self.proc_cmd_line = proc_cmd_line
        prev_pids = get_prev_pids(self_cmd_line)
        print(prev_pids)
        for prev_pid in prev_pids:
            try:
                self.close_proc(prev_pid)
            except:
                pass
        if pid:
            self.proc = psutil.Process(pid)
        
        #假如不存在该cmdline创建的进程，看门狗自动为其创建
        print('WatchDog:\n\tCreating new process...')
        self.proc = psutil.Process(
            pid = self.create_proc().pid
        )

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

    def close_proc(self,ex_pid=None):
        if ex_pid:
            pid = ex_pid
        else:
            pid = self.proc.pid
        print('WatchDog:\n\tKilling process:  {}  ...'.format(pid))
        os.system(
            'kill -9 {}'.format(pid)
        )

    def create_proc(self):
        sp = subprocess.Popen(
            args = self.proc_cmd_line,
            bufsize = 0
        )
        print('WatchDog\n\tThe new pid is {}'.format(sp.pid))
        return sp

    def restart(self):
        self.close_proc()
        self.create_proc()
        self.proc = get_existed_proc(self.proc_cmd_line)
        print('WatchDog:\n\tRestart ok! The new pid is: ' + str(self.proc.pid))

    @property
    def proc_status(self):
        return self.proc.status()

    def run(self):
        pass
        '''
        maybe like that:
            while(1):
                if self.proc_status() is 'sleeping':
                    self.send_mail('fuck')
                time.sleep(timeout)
        '''
