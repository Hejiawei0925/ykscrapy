import re
import time
import json
import urllib.request,urllib.parse
import requests


def log(func):
    def decorator(*args, **kwargs):
        # print(func.__name__+' called')
        return func(*args, **kwargs)
    return decorator

class videolink():
    def __init__(self,vid):
        self.vid = vid
        #print("初始化vid:"+str(vid))

    @log
    def fetch_cna(self):
        url = 'http://log.mmstat.com/eg.js'
        req = self.rq(url)
        headers = req.headers
        cna_pattern = 'cna=(.*?);'
        self.cna = re.findall(cna_pattern,headers['Set-Cookie'])[0]

    @log
    def get_json_url(self):
        ccode = '0516'
        utid = self.cna
        ckey = 'DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND'
        url = 'https://ups.youku.com/ups/get.json?vid={}&ccode={}'.format(self.vid, ccode)
        url += '&client_ip=192.168.1.1'
        url += '&utid=' + utid
        url += '&client_ts=' + str(int(time.time()))
        url += '&ckey=' + urllib.parse.quote(ckey)
        self.json_url = url

    @log
    def get_m3u8_url(self):
        data = self.rq(self.json_url)
        api_meta = json.loads(data.text)
        if 'error' in  api_meta['data']:
            if '版权' in api_meta['data']['error']['note']:
                self.errcode = 1
            else :
                self.errcode = 2
            return False
        else:
            self.cdn_url =api_meta['data']['stream'][0]['segs'][0]['cdn_url']
            self.m3u8_url = api_meta['data']['stream'][0]['m3u8_url']

    @log
    def get_video_url(self):
        m3u8_data  = self.rq(self.m3u8_url)
        if m3u8_data:
            http_pattern = 'http:(.*?)#'
            tslinks = re.findall(http_pattern,m3u8_data.text,re.S)
            self.tslinks = [('http:'+link).strip() for link in tslinks]
            #print(self.vid+str(self.cdn_url)+'?'*20)
            if len(self.tslinks)==0 :
                #print('json:'+self.json_url)
                self.errcode = 3
                return False

    @log
    def api(self):
        self.fetch_cna()
        self.get_json_url()
        if self.get_m3u8_url() == False or self.get_video_url() == False:
            #print(str(self.errcode)*100)
            return self.errcode
        return self.tslinks

    def rq(self,url):
        for i in range(3):
            # print('-'*100)
            # print(str(i)+': '+url)
            try:
                response = requests.get(url=url,timeout=3)
                return response
            except Exception as e:
                print('rq'+str(e))
                return False
                #time.sleep(1)




