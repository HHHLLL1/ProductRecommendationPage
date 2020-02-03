import json
import telnetlib
import requests
import random

proxy_url = 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list'
# proxyList = []

def verify(ip,port,type):
    proxies = {}
    try:
        telnet = telnetlib.Telnet(ip,port=port,timeout=3)
    except:
        print('unconnected')
    else:
        #print('connected successfully')
        # proxyList.append((ip + ':' + str(port),type))
        proxies['type'] = type
        proxies['host'] = ip
        proxies['port'] = port
        proxiesJson = json.dumps(proxies)
        with open('./verified_proxies.json','a+') as f:
            f.write(proxiesJson + '\n')
        print("已写入：%s" % proxies)

def getProxy(proxy_url):
    response = requests.get(proxy_url)
    proxies_list = response.text.split('\n')
    for proxy_str in proxies_list:
        try:
            proxy_json = json.loads(proxy_str)
            host = proxy_json['host']
            port = proxy_json['port']
            type = proxy_json['type']
            verify(host,port,type)
        except:
            pass


if __name__ == '__main__':
    getProxy(proxy_url)
