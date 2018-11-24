# import re
# import time
# import json
# import urllib.request,urllib.parse
# import requests
#
# from scrapy import Request
#
#
# class videolink():
#     def __init__(self,vid):
#         self.vid = vid
#         self.cna_url ='http://log.mmstat.com/eg.js'
#
#     def get_json_url(self,response):
#         x = response.headers['Set-Cookie'].decode().split(';')[0]
#         cna_pattern = 'cna=(.*?);'
#         self.cna = re.findall(cna_pattern,x)[0]
#         ccode = '0516'
#         utid = self.cna
#         ckey = 'DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND'
#         url = 'https://ups.youku.com/ups/get.json?vid={}&ccode={}'.format(self.vid, ccode)
#         url += '&client_ip=192.168.1.1'
#         url += '&utid=' + utid
#         url += '&client_ts=' + str(int(time.time()))
#         url += '&ckey=' + urllib.parse.quote(ckey)
#         self.json_url = url
#         yield  Request(self.json_url,callback=self.get_m3u8_url)
#     def get_m3u8_url(self,response):
#         try :
#             data = response.text
#             api_meta = json.loads(data)
#             m3u8_url = api_meta['data']['stream'][0]['m3u8_url']
#             self.m3u8_url = m3u8_url
#             yield  Request(self.m3u8_url,callback=self.get_video_url)
#         except:
#             pass
#
#     def get_video_url(self,response):
#         try:
#             m3u8_data  = response.text
#             http_pattern = 'http:(.*?)#'
#             tslinks = re.findall(http_pattern,m3u8_data,re.S)
#             self.tslinks = [('http:'+link).strip() for link in tslinks]
#             return self.tslinks
#         except:
#             pass
#
#     def api(self,response):
#         yield Request(self.cna_url,callback=self.get_json_url)

import re
import time
import json
import urllib.request,urllib.parse
import requests


class videolink():
    def __init__(self,vid):
        self.vid = vid
        self.flag = 0
    def fetch_cna(self):
        url = 'http://log.mmstat.com/eg.js'
        try:
            req = self.rq(url)
            headers = req.headers
            cna_pattern = 'cna=(.*?);'
            cna = re.findall(cna_pattern,headers['Set-Cookie'])[0]
            self.cna = cna
        except:
            self.flag = 1


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
            data = self.rq(self.json_url)
            api_meta = json.loads(data.text)
            m3u8_url = api_meta['data']['stream'][0]['m3u8_url']
            self.m3u8_url = m3u8_url
        except:
            print("版权问题"+self.vid)
            self.flag = 1

    def get_video_url(self):
        try:
            m3u8_data  =self.rq(self.m3u8_url)
            http_pattern = 'http:(.*?)#'
            tslinks = re.findall(http_pattern,m3u8_data.text,re.S)
            self.tslinks = [('http:'+link).strip() for link in tslinks]
        except:
            self.flag = 1


    def api(self):
        self.fetch_cna()
        self.get_json_url()
        self.get_m3u8_url()
        self.get_video_url()
        if self.flag == 1:
            return False
        return self.tslinks

    def rq(self,url):
        for i in range(5):
            try:
                response = requests.get(url=url,timeout=3)
                return response
            except Exception as e:
                print(e)
                time.sleep(1)

        self.flag = 1



