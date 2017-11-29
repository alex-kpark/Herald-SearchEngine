# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class NewsCrawlerItem(scrapy.Item):
     #category = scrapy.Field() # 카테고리
     title = scrapy.Field() # 제목
     date = scrapy.Field() # 날짜
     url = scrapy.Field() # 기사링크
     category = scrapy.Field() # 기사링크
     article = scrapy.Field() # 기사링크
     pass

