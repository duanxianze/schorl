#coding:utf-8
'''
    request_with_proxy.py 用于设置爬虫代理
'''

import time
from ua_pool import agents
import requests
requests.packages.urllib3.disable_warnings()
from random import randint
import random,os

if os.name is 'nt':
    No_Prox = True
else:
    No_Prox = False

'''
功能：随机分配端口
传入参数：
    x,y：    随机域的两个边界，
    exclude：以及一个包含所有不可能值的集合对象
返回随机端口
'''
def rand_port(x, y, exclude):
    r = None
    while r in exclude or not r:
        r = randint(x, y)
    return r

'''
功能：发送代理请求
传入参数：
    url：    请求地址url，
    timeout：爬取时间间隔，
    use_ss： 是否使用shadowsocks代理
    sleep:   运行前等待时间
返回请求结果
'''
def request_with_proxy(url, timeout=30, use_ss=False, sleep=10, no_proxy_test=No_Prox):
    headers = {'User-Agent': random.choice(agents)}
    if no_proxy_test:
        return requests.get(url, headers=headers, timeout=timeout)
    time.sleep(sleep)
    r = None
    if not use_ss:
        proxy_port = rand_port(9054, 9155, [])
        proxies = {
                "http": "socks5://127.0.0.1:{}".format(proxy_port),
                "https": "socks5://127.0.0.1:{}".format(proxy_port)
        }
        r = requests.get(url, proxies=proxies, headers=headers, timeout=timeout)
    else:
        port_range = (1080, 1108)
        error_ports = [1094, 1098]
        port = rand_port(1080, 1108, error_ports)
        proxies = {
            "http": "socks5://127.0.0.1:{}".format(port),
            "https": "socks5://127.0.0.1:{}".format(port)
        }
        r = requests.get(url, proxies=proxies, timeout=timeout, headers=headers)

    return r
