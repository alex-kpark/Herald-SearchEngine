#!/bin/bash

path="/media/donghyun/Share/Donghyun/Study/KoreaUniv/2017/2학기/Information Retrieval/프로젝트/Search Engine/Git/engine"

scrapy runspider ./C2_for_URL/spiders/updateSpider_U.py '-odata/new_url.json'  
scrapy runspider ./C1_for_crawl/spiders/newsSpider.py '-odata/new_news.json'

python DBandJson.py

