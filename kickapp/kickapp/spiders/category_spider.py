# Gets the link of each project
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


class CategorySpider(Spider):
    name = "CategorySpider"
    allowed_domains = ["kickstarter.com"]
    start_urls = ["https://www.kickstarter.com/help/stats"]
    
    def parse(self, response):
        sel = Selector(response)
        
        rootdir ="/Users/haruyaishikawa/Desktop/Programming/scraping/kickapp"
        filenames = os.listdir(rootdir)
        
        isafile = 0
        for file in filenames:
            if file == filename:
                isafile = 1
        
        f = open('category.csv', 'ab')
        csvWriter = csv.writer(f)
        
        if isafile == 0:
            print "=============================="
            print "First time scraping:"
            print "I will make a new csv file"
            print "=============================="
            