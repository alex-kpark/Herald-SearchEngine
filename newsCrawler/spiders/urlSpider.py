
import scrapy
from newsCrawler.items import NewsCrawlerItem

class NewsUrlSpider(scrapy.Spider):
    name = "urlSpider"

    def start_requests(self):
        # 순서대로 National, Business, Life&Style, Entertainment, Sports, World, Opinion
        urls =  [ 'http://www.koreaherald.com/list.php?ct=020100000000&ctv=0&np=',
                  'http://www.koreaherald.com/list.php?ct=020200000000&ctv=0&np=',
                  'http://www.koreaherald.com/list.php?ct=020300000000&ctv=0&np=',
                  'http://www.koreaherald.com/list.php?ct=020400000000&ctv=0&np=',
                  'http://www.koreaherald.com/list.php?ct=020500000000&ctv=0&np=',
                  'http://www.koreaherald.com/list.php?ct=021200000000&ctv=0&np=',
                  'http://www.koreaherald.com/list.php?ct=020600000000&ctv=0&np=']
        for u in urls:
            for i in range (1,3188): # range 범위:National= 3144, Business= 2995, Life&Style= 926, Entertainment=868, Sports=638, World=1388, Opinion= 920
                 yield scrapy.Request(url= u + str(i) , callback=self.parse)

    def parse(self, response):
        for path in response.xpath('body/div/div[3]/div[2]/div/ul[1]/li'):   
                item = NewsCrawlerItem()
                item['url'] = path.xpath('//div[2]/p[1]/a/@href').extract()

 
        yield item
