import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent

port_range = (1080, 1097)
port_list = [x for x in range(port_range[0], port_range[1]+1)]
error_port = [1083, 1085, 1089, 1094]

ua = UserAgent()
headers = {'user-agent': ua.random}
'''

while True:
    for port in port_list:
        print(port)
        if port in error_port:
            continue
        proxies = {
            "http": "socks5://127.0.0.1:{}".format(port),
            "https": "socks5://127.0.0.1:{}".format(port)
        }
        r = requests.get("https://scholar.google.com/scholar?start=0&q=John+Booske&hl=en&as_sdt=0,5", proxies=proxies, timeout=5)
        print(r.text)
        if port == port_list[-1]:
            break
'''
def test_port(port_num):
    proxies = {
        "http": "socks5://127.0.0.1:{}".format(port_num),
        "https": "socks5://127.0.0.1:{}".format(port_num)
    }
    r = requests.get("https://api.ipify.org/", proxies=proxies, timeout=5, headers=headers)
    print(r.text)

for i in range(1080, 1108):
    try:
        test_port(i)
    except Exception as e:
        print(i)
        print(e)
