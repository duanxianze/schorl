#coding:utf-8
"""
@file:      DriversPool.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-04 0:32
@description:
            selenium webdriver的pool类，封装staus和index
"""
import time
from selenium import webdriver

class Driver:
    def __init__(self,visual,index):
        self.index = index
        self.status = 'free'
        if visual:
            self.engine = webdriver.Chrome()
        else:
            self.engine = webdriver.PhantomJS()


class DriversPool:
    def __init__(self,size=4):
        self.size = size
        self.pool = []
        self.create()

    def create(self):
        for i in range(self.size):
            print("DriversPool:\n\tLaunching Engine-{}...".format(i))
            self.pool.append(
                Driver(visual=True,index=i)
            )

    def alter_driver_status(self,index,status):
        self.pool[index].status = status

    def get_one_free_driver(self,wait=False):
        while(1):
            for driverObj in self.pool:
                if driverObj.status is 'free':
                    return driverObj
            if wait:
                print('DriversPool:\n\tSorry, no FREE driver now.\n\t Search again in ten seconds...')
                time.sleep(10)
            else:
                break
        return None

    def tear_down(self):
        for driverObj in self.pool:
            driverObj.engine.close()