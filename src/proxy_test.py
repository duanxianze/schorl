import requests
requests.packages.urllib3.disable_warnings()
import socket
import socks
from random import randint

rand_port = lambda x, y: randint(x, y)

while True:
    proxy_port = rand_port(9053, 9113)
    print(proxy_port)
    socks.set_default_proxy(socks.SOCKS5, "localhost", proxy_port)
    socket.socket = socks.socksocket

    r = requests.get('https://api.ipify.org', verify=False)
    print(r.text)
