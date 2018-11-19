import re
import time
import json
import urllib.request,urllib.parse
import requests


class videolink():
    def __init__(self,vid):
        self.vid = vid
    def fetch_cna(self):
        url = 'http://log.mmstat.com/eg.js'
        try:
            req = requests.get(url)
            headers = req.headers
            cna_pattern = 'cna=(.*?);'
            cna = re.findall(cna_pattern,headers['Set-Cookie'])[0]
            #print('cna'+cna)
            self.cna = cna
        except:
            cna = self.fetch_cna()
            self.cna = cna

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

    def get_m3u8_url(self):
        try :
            data = requests.get(self.json_url)
            api_meta = json.loads(data.text)
            m3u8_url = api_meta['data']['stream'][0]['m3u8_url']
            self.m3u8_url = m3u8_url
        except:
            print(self.json_url+'请求失败！！！')
            pass
            #self.get_m3u8_url()

    def get_video_url(self):
        try:
            m3u8_data  =requests.get(self.m3u8_url)
            http_pattern = 'http:(.*?)#'
            tslinks = re.findall(http_pattern,m3u8_data.text,re.S)
            self.tslinks = [('http:'+link).strip() for link in tslinks]
        except:
            pass

    def api(self):
        self.fetch_cna()
        self.get_json_url()
        self.get_m3u8_url()
        self.get_video_url()
        return self.tslinks


