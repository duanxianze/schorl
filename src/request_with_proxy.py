#coding:utf-8
'''
    request_with_proxy.py 用于设置爬虫代理
'''

import requests
import time
from fake_useragent import UserAgent
import requests
requests.packages.urllib3.disable_warnings()
from random import randint
import socks
import socket

ua = UserAgent()

'''
功能：随机分配端口
传入参数：随机域的两个边界x,y，以及一个包含所有不可能值的集合对象exclude
'''
def rand_port(x, y, exclude):
    r = None
    while r in exclude or not r:
        r = randint(x, y)
    return r

'''
功能：发送代理请求
传入参数：请求地址url，爬取时间间隔timeout，
        是否使用shadowsocks代理use_ss
返回请求结果
'''
def request_with_proxy(url, timeout=10, use_ss=True):
    time.sleep(30)
    headers = {'User-Agent': ua.random}
    r = None
    if not use_ss:
        proxy_port = rand_port(9054, 9155)
        proxies = {
                "http": "socks5://127.0.0.1:{}".format(proxy_port),
                "https": "socks5://127.0.0.1:{}".foramt(proxy_port)
        }
        r = requests.get(url, proxies=proxies, headers=headers, timeout=20)
    else:
        port_range = (1080, 1097)
        error_ports = [1083, 1085, 1089, 1094]
        port = rand_port(1080, 1097, error_ports)
        proxies = {
            "http": "socks5://127.0.0.1:{}".format(port),
            "https": "socks5://127.0.0.1:{}".format(port)
        }
        r = requests.get(url, proxies=proxies, timeout=20, headers=headers)

    print(r.status_code)

    return r
