#!/bin/bash

cd /home/webmanager/spider/kickapp/
/home/webmanager/anaconda2/bin/scrapy crawl RateSpider
/home/webmanager/anaconda2/bin/scrapy crawl LiveSpider

zip -r "archive/"`date "+%Y%m%d"` data.csv projects/

