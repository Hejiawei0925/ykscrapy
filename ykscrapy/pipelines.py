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
        item['owner'] = item['owner'].strip()
        settings = get_project_settings()
        root_dir = settings['FILES_STORE']
        try:
            rpath = item['files'][0]['path'].split('/')[1]
        except:
            item['path'] = '无'
            return item

        path = root_dir + '/' + item['dir'] +'/'+rpath
        item['path'] = path
        cmd = 'cd %s && copy /b *.ts new.mp4 && del *.ts '%(path)
        os.system(cmd)
        return item

class VideoPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        return [Request(x,meta={
                                'title':item['title'],
                                'dir':item['dir'],
                                }) for x in item.get(self.files_urls_field, [])]

    def file_path(self, request, response=None, info=None):
        #resquest.meta response.meta 有什么区别？
        dir = request.meta['dir']
        new_title = request.meta['title']
        n_pattern = 'ts_seg_no=(.*?)&'
        if 'ts_seg_no=' in request.url:
            number = re.findall(n_pattern,request.url)[0]
            number = str(number).zfill(4)
            return '%s/%s/%s.ts' % (dir,new_title,number)
        else :
            return '%s/%s/%s.ts' % (dir,new_title,'1')

