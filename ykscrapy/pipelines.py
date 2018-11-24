# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class YkscrapyPipeline(object):
#     def process_item(self, item, spider):
#
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.project import get_project_settings

from scrapy import Request
import re
import os
import sys
import pymysql
from scrapy.conf import settings

from twisted.enterprise import adbapi
class DBPipeline():
    def process_item(self, item, spider):
        db =pymysql.connect('127.0.0.1','root','root',db='ykspider')
        cursor = db.cursor()

        data = {
            'vid' : item['vid'],
            'title': item['title'],
            'url':item['url'],
            'comment':item['comments'],
            'score':item['score'],
            'author':item['owner'],
            'up_time':item['up_time'],
            'tag':item['tag'],
            'path':item['path'],
        }

        table = 'video_info'

        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'INSERT INTO {table} ({keys}) VALUES ({values})'.format(table=table,keys=keys,values=values)

        try:
            if cursor.execute(sql,tuple(data.values())):
                db.commit()
        except:
            db.rollback()
        db.close()
        return item


class YkitemPipeline():
   def process_item(self, item, spider):
        settings = get_project_settings()
        dir = settings['FILES_STORE']
        try:
            rpath = item['files'][0]['path'].split('/')[0]
        except:
            item['path'] = '无'
            return item
        path = dir+'/'+rpath
        item['path'] = path
        cmd = 'cd %s && copy /b *.ts new.mp4 && del *.ts '%(path)
        os.system(cmd)

        if item['score'] == []:
            item['score'] = '无'
        else :
            item['score'] = item['score'][0].text

        # tags = []
        # if item['tag'] == []:
        #     item['tag'].append('无')
        # else :
        #     for t in item['tag']:
        #         tags.append(t.text)
        #         item['tag'].clear()
        #         item['tag'] = tags[:]
        #item['tag'] = str(item['tag'])

        item['owner'] = item['owner'].strip()
        return item

class VideoPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        return [Request(x,meta={'title':item['title']}) for x in item.get(self.files_urls_field, [])]

    def file_path(self, request, response=None, info=None):
        #resquest.meta response.meta 有什么区别？
        new_title = request.meta['title']
        n_pattern = 'ts_seg_no=(.*?)&'
        number = re.findall(n_pattern,request.url)[0]
        return '%s/%s.ts' % (new_title,number)






'''
title
if(len(x)!=0):
            title = x[0]
        else:
            title="???"

        title = re.sub('[^\w\s]','',title)
        video['title'] =  title.replace(' ','_')
        
score      
if scores == []:
            video['score'] = '无'
        else :
            video['score'] = scores[0].text   
            
tag         
tags = soup.find_all(class_='v-tag')
        video['tag'] = []
        if tags == []:
            video['tag'].append('无')
        else :
            for t in tags:
                video['tag'].append(t.text)  
owner                
 owner = soup.select('#module_basic_sub > a:nth-of-type(1)')[0].text
        video['owner'] = owner.strip()   
'''