# Scrapes the currency function from 
#
# -*- coding: utf-8 -*-
import scrapy

## other modules
import sys
import glob, os
import csv
import time

## scrapy module things
from scrapy.spiders import Spider
from scrapy.selector import Selector
from kickapp.items import KickappItem

class RateSpider(Spider):
        name = "RateSpider"
        allowed_domains = ["xe.com"]
        start_urls = ["http://www.xe.com/currencytables/?from=USD"]
        
        def parse(self, response):
            sel = Selector(response)
            ##============================================================================##
            rootdir = os.environ['PWD'] + '/rates'
            ##============================================================================##
            
            currencies = sel.xpath('//*[@id="historicalRateTbl"]/tbody/tr[*]')
            
            for currency in currencies:
                name = currency.xpath('td[1]/a/text()').extract()[0].encode("ascii", "ignore")
                rate = currency.xpath('td[4]/text()').extract()[0].encode("ascii", "ignore")
                rate = float(rate)
                filename = name.lower() + '.csv'
                
                ## deletes the rates everyday and rewrites it
                f = open(rootdir+'/'+filename, 'w+')
                csvWriter = csv.writer(f)
                csvWriter.writerow([rate])
                f.close()
                
            rootdir = '/Users/haruyaishikawa/Desktop/Programming/scraping/beausoup/crawler/rates'
            for currency in currencies:
                name = currency.xpath('td[1]/a/text()').extract()[0].encode("ascii", "ignore")
                rate = currency.xpath('td[4]/text()').extract()[0].encode("ascii", "ignore")
                rate = float(rate)
                filename = name.lower() + '.csv'
                
                ## deletes the rates everyday and rewrites it
                f = open(rootdir+'/'+filename, 'w+')
                csvWriter = csv.writer(f)
                csvWriter.writerow([rate])
                f.close()
                