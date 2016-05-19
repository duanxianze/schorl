import requests
import time
from fake_useragent import UserAgent
import requests
requests.packages.urllib3.disable_warnings()
from random import randint
import socks
import socket

ua = UserAgent()

rand_port = lambda x, y: randint(x, y)

def request_with_proxy(url, timeout=10):
    headers = {'User-Agent': ua.random}
    proxy_port = rand_port(9053, 9113)
    socks.set_default_proxy(socks.SOCKS5, "localhost", proxy_port)
    socket.socket = socks.socksocket
    r = requests.get(url, headers=headers)
    while str(r.status_code).startswith('5') or str(r.status_code).startswith('4'):
        print(r.status_code)
        print('retrying...')
        request_with_proxy(url)
    return r

