from scrapy import Request
import scrapy
from bs4 import BeautifulSoup
import re
import json
from ..items import YkscrapyItem
from VideoUrl import videolink

class YoukuSpider(scrapy.Spider):
    name = 'youku'
    topic = ['jkjs']#,'jkjs','jsqy','sxbk','mcdb']
    start_urls = ['http://news.youku.com/index/%s'%x for x in topic]
    num = 2
    MAX_PAGENUM = 2

    def parse(self,response):
        soup = BeautifulSoup(response.text,'lxml')
        urls = soup.select('div.v-meta-title > a')

        for url in urls:
            url = 'http:'+url.get('href')
            yield Request(url,callback=self.video_page_parse)

        id_pattern = 'name="m_pos" id="m_(.*?)"'
        id = re.findall(id_pattern,response.text)[0]
        if self.num < self.MAX_PAGENUM:
            self.num += 1
            nav_url = response.url+'/_page%s_%d_cmodid_%s'%(id,self.num,id)
            yield Request(nav_url)

    def video_page_parse(self,response):
        video = YkscrapyItem()
        video['url'] = response.url
        title_pattern = '<meta name="title" content="(.*?)" />'
        x = re.findall(title_pattern,response.text)
        if(len(x)!=0):
            title = x[0]
        else:
            title="???"

        title = re.sub('[^\w\s]','',title)
        video['title'] =  title.replace(' ','_')

        soup = BeautifulSoup(response.text,'lxml')
        scores = soup.select('div > h2 > span')
        if scores == []:
            video['score'] = '无'
        else :
            video['score'] = scores[0].text
        tags = soup.find_all(class_='v-tag')
        video['tag'] = []
        if tags == []:
            video['tag'].append('无')
        else :
            for t in tags:
                video['tag'].append(t.text)
        #self.tag = str(self.tag)
        owner = soup.select('#module_basic_sub > a:nth-of-type(1)')[0].text
        video['owner'] = owner.strip()
        video['up_time']= soup.find_all(class_='bold mr3')[0].text
        vid_pattern = "videoId: '(.*?)'"
        try :
            video['vid'] = re.findall(vid_pattern,response.text)[0]
        except IndexError:
            video['vid'] ='0'
            print(video['url']+'列表出错')
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
            #print(i['content'])
            comments.append(comment)

        video['comments'] = comments

        x = self.video_parse(video)

        yield x

    def video_parse(self,video):
        t = videolink(video['vid'])
        vurls = t.api()
        video['file_urls'] = vurls
        return video

