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
            input_infos = json.load(fp)
            for input_key in input_infos.keys():
                if input_key in self.info_dict.keys():
                    self.info_dict[input_key] = input_infos[input_key]
                else:
                    raise Exception(
                        'DB_Config: <{}> is invalid key'.format(input_key)
                    )

    def get_info_dict(self):
        self.generate()
        return self.info_dict
