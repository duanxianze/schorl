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


class WatchDog:
    '''
        对于每个process(对应于每个任务)的监视管理器
        如果需要定制，可做父类继承
    '''
    def __init__(self,cmd_line,task_proc_cmd_line,pid=None):
        self.cmd_line = cmd_line
        self.task_proc_cmd_line = task_proc_cmd_line
        self.kill_prev_watchdog_procs()#清理之前的类似看门狗进程
        if pid:
            #直接以pid初始化task_proc
            self.task_proc = psutil.Process(pid)
        else:
            #未指定已存在的子进程id，看门狗自动为其创建
            self.kill_prev_task_procs()
            self.create_new_task_proc()
            print('WatchDog:\n\tThe new pid is : {}'.format(self.task_proc.pid))

    def kill_prev_watchdog_procs(self):
        prev_pids = get_prev_pids(self.cmd_line)[:-1]
        print('WatchDog:\n\tPrevious watchdog pids: {}'.format(prev_pids))
        #清理之前的看门狗进程
        close_procs(prev_pids)

    def kill_prev_task_procs(self):
        prev_pids = get_prev_pids(self.task_proc_cmd_line)
        print('WatchDog:\n\tPrevious task pids: {}'.format(prev_pids))
        #清理之前的看门狗进程
        close_procs(prev_pids)

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

    def close_task_proc(self):
        print('WatchDog:\n\tKilling process:  {}  ...'.format(self.task_proc.pid))
        os.kill(self.task_proc.pid,9)

    def create_new_task_proc(self):
        print('WatchDog:\n\tCreating new task_process...')
        self.task_proc = psutil.Process(
            pid = subprocess.Popen(
                args = self.task_proc_cmd_line,
                bufsize = 0
            ).pid
        )

    def restart_task_proc(self):
        self.close_task_proc()
        self.create_new_task_proc()
        print('WatchDog:\n\tRestart ok! The new pid is: ' + str(self.task_proc.pid))

    @property
    def task_proc_status(self):
        try:
            return self.task_proc.status()
        except:
            return 'dead'
    '''
    def run(self):
        pass

        maybe like that:
            while(1):
                if self.proc_status() is 'sleeping':
                    self.send_mail('fuck')
                time.sleep(timeout)
    '''



'''
    funcs of process tools...
'''

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
    #print('cmd_line',cmd_line)
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
    return prev_pids


def close_procs(pids):
    for pid in pids:
        try:
            os.kill(pid,9)
            print (
                '\tKill pid:{} ok!'.format(pid)
            )
        except:
            pass