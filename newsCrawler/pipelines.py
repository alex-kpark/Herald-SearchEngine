# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#CVS파일로 저장하는 클래스
from __future__ import unicode_literals
from scrapy.exporters import JsonItemExporter, CsvItemExporter

    
class JsonPipeline(object):
    def __init__(self):
        self.file = open("NC_70mb.json", 'wb')
        #self.file = open("NUC_70mb.json", 'wb')
        #newsSpider돌릴 시 "newsCrawl.json"으로 변경
        #urlSpider돌릴 시 "newsUrlCrawl.json"
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

#사용하지 않음
class NewscrawlerPipeline(object):
    def __init__(self):
        self.file = open("newsUrlCrawl.csv", 'wb')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8')
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

