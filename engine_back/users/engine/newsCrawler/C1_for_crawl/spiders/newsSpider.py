import scrapy
import csv
import json
import re
import regex
from items import NewsCrawlerItem

class NewsSpider(scrapy.Spider):
    name = "newsSpider"

    def start_requests(self):

       with open ('./data/new_url.json') as jsonfile:
           reader = json.load(jsonfile)
           for rdr in reader:
               for url in rdr["url"]:
                   yield scrapy.Request('http://www.koreaherald.com' + url, callback = self.parse_news)

    def parse_news(self, response):
        regex = r'[가-힣]+'
        tmppicture =''.join(response.xpath('//*[@id="articleText"]/table/tbody/tr/td/font/text()').extract())
        tmppicture2 = ''.join(response.xpath('//*[@id="articleText"]/center/div/p/text()').extract())
        tmparticle = ''.join(response.xpath('//*[@id="articleText"]/text()').extract())
        tmparticle2 = ''.join(response.xpath('//*[@id="articleText"]/p/text()').extract())
        tmparticle3 =  ''.join(response.xpath('//*[@id="articleText"]/p/span/text()').extract())
        tmparticle4 =  ''.join(response.xpath('//*[@id="articleText"]/div/text()').extract())
        tmparticle5 =  ''.join(response.xpath('//*[@id="articleText"]/p/font/text()').extract())
        tmparticle6 =  ''.join(response.xpath('//*[@id="articleText"]/p/span/font/font/text()').extract())
        tmparticle = tmparticle + ' ' + tmparticle2 + ' ' + tmparticle3 + ' ' + tmparticle4 + ' ' + tmparticle5 + ' ' + tmparticle6 + ' ' + tmppicture + ' ' + tmppicture2
        result = re.findall(regex, tmparticle)
        #for word in result:
        #    tmparticle = tmparticle.replace(word,"")
        tmparticle = re.sub('[!"#%\'()*+\t\r\n/:;<=>?@\[\]\\xa0$^_`{|}~’”“′‘\\\]',' ', tmparticle)
        #tmparticle = re.sub('[!"#%\'()*+,./:;<=>?@\[\]\\xa0^_`{|}~’”“′‘\\\]',' ', tmparticle)
        tmparticle = tmparticle.replace(",","")
        tmparticle = tmparticle.replace(".","")
        tmparticle = tmparticle.replace("--","")
        tmparticle = " ".join(tmparticle.split())
        #for word in result:
        if result ==[] :
            if tmparticle != "" :
                item = NewsCrawlerItem()
                item['article'] = tmparticle
                tmptitle = response.xpath('body/div[1]/div[3]/div[2]/div/div[1]/div[3]/p[1]/text()').extract()
                item['title'] = ''.join( tmptitle)
                tmpurl= str(response)
                item['url'] = tmpurl[12:58]
                item['date'] = tmpurl[44:52]
                tmpcategory = response.xpath('body/div[1]/div[3]/div[2]/div/div[1]/p/text()').extract()
                item['category'] = ''.join(tmpcategory)

        yield item

