import scrapy
import csv
import json
from newsCrawler.items import NewsCrawlerItem

class NewsSpider(scrapy.Spider):
    name = "newsSpider"

    def start_requests(self):
       with open ('news.json') as jsonfile:
           reader = json.load(jsonfile)
           for rdr in reader:
               for url in rdr["url"]:
                   yield scrapy.Request('http://www.koreaherald.com' + url, callback = self.parse_news)
        
    def parse_news(self, response):
        item = NewsCrawlerItem()
        tmptitle = response.xpath('body/div[1]/div[3]/div[2]/div/div[1]/div[3]/p[1]/text()').extract()
        item['title'] = ''.join( tmptitle)
        tmpurl= str(response)
        item['url'] = tmpurl[12:58]
        item['date'] = tmpurl[44:52]
        
        tmpcategory = response.xpath('body/div[1]/div[3]/div[2]/div/div[1]/p/text()').extract()
        item['category'] = ''.join(tmpcategory)
        tmparticle = ''.join(response.xpath('//*[@id="articleText"]/text()').extract())
        tmparticle = tmparticle.replace("\t","")
        tmparticle = tmparticle.replace("\n","")
        tmparticle = tmparticle.replace("\r","")
        item['article'] = tmparticle.replace("\"","")
        yield item
