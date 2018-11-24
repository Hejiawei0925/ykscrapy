# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class YkscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    vid = Field()
    vid2 = Field()
    title = Field()
    url = Field()
    comments = Field()
    score = Field()
    owner = Field()
    up_time = Field()
    tag = Field()
    dir = Field()
    path = Field()
    file_urls = Field()
    files = Field()

