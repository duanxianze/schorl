#coding:utf-8
"""
@file:      push_file_to_group
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-08 17:38
@description:
            --
"""

from crawl_tools.ScpToGroup import ScpToGroup

ScpToGroup(
    local_path='../',
    remote_path='~/',
    config_folder_path='./group_configs',
    is_folder=True
).push()