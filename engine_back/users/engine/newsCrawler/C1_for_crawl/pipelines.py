# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from scrapy.exporters import JsonItemExporter, CsvItemExporter

    
class JsonPipeline(object):
    def __init__(self):
        self.file = open("./data/new_news.json", 'wb') #updateSpider_N 사용시
        #self.file = open("updateUrl.json", 'wb') #updateSpider_U 사용시
        #self.file = open("news.json", 'wb') #newSpider 사용시
        #self.file = open("url.json", 'wb') #urlSpider 사용시
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
