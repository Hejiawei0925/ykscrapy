import re
import json
import requests

def log(func):
    def decorator(*args, **kwargs):
        #print(func.__name__+' called')
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
        self.json_url = 'https://ups.youku.com/ups/get.json?vid=%s&ccode=0405&client_ip=0.0.0.0&client_ts=1543553721&utid=%s'%(self.vid,self.cna)

    @log
    def get_m3u8_url(self):
        data = self.rq(self.json_url)
        api_meta = json.loads(data.text)
        if 'error' in  api_meta['data']:
            if '版权' in api_meta['data']['error']['note']:
                # print("版权")
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
                print('json:'+self.json_url)
                print("m3u8空")
                self.errcode = 3
                return False

    @log
    def api(self):
        self.fetch_cna()
        self.get_json_url()
        if self.get_m3u8_url() == False or self.get_video_url() == False:
            return self.errcode
        return self.tslinks

    def rq(self,url):
        for i in range(3):
            try:
                response = requests.get(url=url,timeout=3)
                return response
            except Exception as e:
                print('rq'+str(e))
                return False

#x = videolink('XMzkyMTk1NzQ0MA')