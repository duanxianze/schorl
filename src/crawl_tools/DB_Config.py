#coding:utf-8
"""
@file:      DB_Config
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-07 20:12
@description:
            通过json转db的配置(python字典)
"""

import json

class DB_Config:
    '''
        use： DB_Config('xx.json').info_dict
    '''
    def __init__(self,json_file_path):
        self.info_dict = {
            'db_name':      None,
            'user' :        None,
            'password' :    None,
            'host' :        None,
            'port' :        None,
            "local_pool_size":   20,
            "remote_pool_size":  5,
            "master_db_in":       False
        }#default values
        self.json_file_path = json_file_path
        self.generate()

    def generate(self):
        with open(self.json_file_path, 'r') as fp:
            infos = json.load(fp)
            for key in infos.keys():
                self.info_dict[key] = infos[key]

    def get_info_dict(self):
        self.generate()
        return self.info_dict
