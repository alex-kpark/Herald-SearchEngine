# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy
from newsCrawler.items import NewsCrawlerItem

class NewsUrlSpider(scrapy.Spider):
    name = "urlSpider"

    def start_requests(self):
        # 순서대로 National, Business, Life&Style, Entertainment, Sports, World, Opinion
        #(urls = 'http://www.koreaherald.com/list.php?ct=020100000000&ctv=0&np='
        # urls = 'http://www.koreaherald.com/list.php?ct=020200000000&ctv=0&np='
        # urls = 'http://www.koreaherald.com/list.php?ct=020300000000&ctv=0&np='
        # urls = 'http://www.koreaherald.com/list.php?ct=020400000000&ctv=0&np='
        # urls = 'http://www.koreaherald.com/list.php?ct=020500000000&ctv=0&np='
        # urls ='http://www.koreaherald.com/list.php?ct=021200000000&ctv=0&np='
        # urls ='http://www.koreaherald.com/list.php?ct=020600000000&ctv=0&np=' )
        urls =  [ 'http://www.koreaherald.com/list.php?ct=020300000000&ctv=0&np=',
                    'http://www.koreaherald.com/list.php?ct=020400000000&ctv=0&np=',
                    'http://www.koreaherald.com/list.php?ct=020500000000&ctv=0&np=',
                    'http://www.koreaherald.com/list.php?ct=021200000000&ctv=0&np=',
                    'http://www.koreaherald.com/list.php?ct=020600000000&ctv=0&np=']
        for u in urls:
            for i in range (1,1388): # range 범위:National= 3144, Business= 2995, Life&Style= 926, Entertainment=868, Sports=638, World=1388, Opinion= 920
                 yield scrapy.Request(url= u + str(i) , callback=self.parse)

    def parse(self, response):
        for path in response.xpath('body/div/div[3]/div[2]/div/ul[1]/li'):   
                item = NewsCrawlerItem()
            
                #item['title'] = path.xpath('//div[2]/p[1]/a/text()').extract()
                item['url'] = path.xpath('//div[2]/p[1]/a/@href').extract()
                #item['url'] = 'http://www.koreaherald.com' + item['url'][i]
                #item['date'] = path.xpath('//li/div[3]/p/text()').extract()


 
        yield item

