from scrapy import Request
import scrapy
from bs4 import BeautifulSoup
import re
import json
from ..items import YkscrapyItem
from vu1 import videolink

import time
class YoukuSpider(scrapy.Spider):
    name = 'youku'
    topic = ['jrrm','jkjs','jsqy','sxbk','mcdb']
    start_urls = ['http://news.youku.com/index/%s'%x for x in topic]
    num = 2
    MAX_PAGENUM = 2

    def parse(self,response):
        soup = BeautifulSoup(response.text,'lxml')
        urls = soup.select('div.v-meta-title > a')
        dir = response.url.split('/')[-1]
        for url in urls:
            url = 'http:'+url.get('href')
            yield Request(url,callback=self.video_page_parse,meta={'dir':dir})

        id_pattern = 'name="m_pos" id="m_(.*?)"'
        id = re.findall(id_pattern,response.text)[0]
        if self.num < self.MAX_PAGENUM:
            self.num += 1
            nav_url = response.url+'/_page%s_%d_cmodid_%s'%(id,self.num,id)
            yield Request(nav_url)

    def video_page_parse(self,response):
        video = YkscrapyItem()
        video['dir'] = response.meta['dir']
        video['url'] = response.url
        title_pattern = '<meta name="title" content="(.*?)" />'
        x= re.findall(title_pattern,response.text)
        if(len(x)!=0):
            title = x[0]
        else:
            title="???"
        title = re.sub('[^\w\s]','',title)
        video['title'] =  title.replace(' ','_')
        soup = BeautifulSoup(response.text,'lxml')

        video['score'] = soup.select('div > h2 > span.score')

        if len(video['score']) == 0:
            video['score'] = '无'
        else :
            video['score'] = video['score'][0].text

        # video['tag'] = str(soup.find_all(class_='v-tag'))

        tags = soup.find_all(class_='v-tag')

        video['tag'] = []
        if len(tags) == 0:
            video['tag'].append('无')
        else :
            for t in tags:
                video['tag'].append(t.text)
        video['tag'] = " ".join(video['tag'])
        video['owner'] = soup.select('#module_basic_sub > a:nth-of-type(1)')[0].text
        video['up_time']= soup.find_all(class_='bold mr3')[0].text
        vid_pattern = "videoId: '(.*?)'"
        vid2_pattern = "videoId2: '(.*?)'"

        try :
            video['vid'] = re.findall(vid_pattern,response.text)[0]
            video['vid2'] = re.findall(vid2_pattern,response.text)[0]

        except IndexError:
            video['vid'] ='0'
            video['vid2'] ='0'
            return

        comment_page = 'http://p.comments.youku.com/ycp/comment/pc/commentList?' \
                             'app=100-DDwODVkv&objectId=%s&listType=0' \
                            '&sign=979b304e50791fe50dc7adeaa67eee48&time=1537438670'%(video['vid'])
        yield Request(comment_page,callback=self.comment_parse,meta={'video':video})

    def comment_parse(self,response):
        video = response.meta['video']
        comments = []
        api_meta = json.loads(response.text)
        for item in api_meta['data']['comment']:
            comment = '#'+item['content']+'##'
            comments.append(comment)
        video['comments'] = str(comments)

        x = self.video_parse(video)
        yield x

    def video_parse(self,video):
        # x = 0
        while True:
            # print(str(x)*200)
            # x += 1
            t = videolink(video['vid2'])
            result = t.api()
            if  result == 1:
                return video
            elif result == 2:
                #print('cndy'*100)
                continue
            elif result == 3:
                video['file_urls'] = t.cdn_url.split()
                return video
            else:
                video['file_urls'] = t.tslinks
                return video
        #return video

