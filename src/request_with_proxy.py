import requests
import time
from fake_useragent import UserAgent
import requests
requests.packages.urllib3.disable_warnings()
from random import randint
import socks
import socket

ua = UserAgent()

def rand_port(x, y, exclude):
    r = None
    while r in exclude or not r:
        print(r)
        r = randint(x, y)
    return r


def request_with_proxy(url, timeout=10, use_ss=True):
    time.sleep(10)
    headers = {'User-Agent': ua.random}
    r = None
    if not use_ss:
        proxy_port = rand_port(9053, 9113)
        socks.set_default_proxy(socks.SOCKS5, "localhost", proxy_port)
        socket.socket = socks.socksocket
        r = requests.get(url, headers=headers)
        while str(r.status_code).startswith('5') or str(r.status_code).startswith('4'):
            print(r.status_code)
            print('retrying...')
            request_with_proxy(url)
    else:
        port_range = (1080, 1097)
        error_ports = [1083, 1085, 1089, 1094]

        port = rand_port(1080, 1097, error_ports)
        proxies = {
            "http": "socks5://127.0.0.1:{}".format(port),
            "https": "socks5://127.0.0.1:{}".format(port)
        }
        time.sleep(10)
        r = requests.get(url, proxies=proxies, timeout=10, headers=headers)

    return r
