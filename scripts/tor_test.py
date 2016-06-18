import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent

'''
port_range = (1080, 1097)
port_list = [x for x in range(port_range[0], port_range[1]+1)]
error_port = [1083, 1085, 1089, 1094]
'''

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
    r = requests.get("https://api.ipify.org/", proxies=proxies, timeout=20, headers=headers)
    return r.text

duplicate = 0
error = 0
ip_list = []
for i in range(9054, 9154):
    try:
        ip = test_port(i)
        print(ip)
        if ip not in ip_list:
            ip_list.append(ip)
        else:
            duplicate += 1
    except Exception as e:
        error += 1
        print(i)
        print(e)

print("duplicate " + str(duplicate))
print("how many ips can be used " + str(len(ip_list)))
print("how many ips can not be used " + str(error))
