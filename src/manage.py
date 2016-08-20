#coding:utf-8
"""
@file:      manage.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-19 15:02
@description:
            lanuch spider
"""
import subprocess

cmd_list = [
    'nohup python task.py &',
    'nohup python auto_dump.py &',
    'nohup python status_monitor.py &'
]

for command in cmd_list:
    subprocess.Popen(command)