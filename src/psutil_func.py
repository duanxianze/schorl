#coding:utf-8
"""
@file:      psutil_func.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-20 0:07
@description:
            --
"""
import psutil


def get_proc_by_name(pname):
    """ get process by name

    return the first process if there are more than one
    """
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == pname.lower():
                return proc  # return if found one
        except psutil.AccessDenied:
            pass
        except psutil.NoSuchProcess:
            pass
    return None