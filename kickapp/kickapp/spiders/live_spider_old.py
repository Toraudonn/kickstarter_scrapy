# Scrapes the data from Live projects
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


class LiveSpiderOld(Spider):
    name = "LiveSpiderOld"
    allowed_domains = ["kickstarter.com"]
    
    ## if anything goes wrong use the number below
    ## and comment out some of the code below
    end_page = 50
    
    ## request the site for the number of pages
    def start_requests(self):
        yield scrapy.Request("https://www.kickstarter.com/discover/advanced?state=live&category_id=16&sort=newest&seed=2444597&page=1", self.parse_init)
        
        
    def parse_init(self, response):
        sel = Selector(response)
        some_text = sel.xpath('//*[@id="projects"]/div[2]/h3/b/text()').extract()[0].encode("ascii", "ignore")
        
        ## got the number of pages
        print "================================================="
        print some_text
        end_page = int(some_text.split()[0])/20 + 1
        print "total number of pages: " + str(end_page) 
        print "================================================="
        
        ## start scraping
        urls = ["https://www.kickstarter.com/discover/advanced?state=live&category_id=16&sort=newest&seed=2444597&page=%d" %(n) for n in range (1,end_page+1)]
        for url in urls:
            ## when dont_filter is false, it filters page=1 
            yield scrapy.Request(url, callback=self.parse, dont_filter = True)
            
    ## edit the xpath for the things I need
    def parse(self, response):
        #print response.url
        ## setting up the rootdir of the projects files
        rootdir = "/Users/haruyaishikawa/Desktop/Programming/scraping/kickapp/projects"
        filenames = os.listdir(rootdir)
        
        sel = Selector(response)
        projects = sel.xpath('//*[@id="projects_list"]/*/*/div')
        ## opening ref.csv file
        f = open('ref.csv','ab')
        csvWriter = csv.writer(f)
        
        for project in projects:
            title = project.xpath('div[2]/h6/a/text()').extract()[0].encode("ascii", "ignore")
            url = project.xpath('div[2]/h6/a/@href').extract()[0].encode("ascii", "ignore")
            separater = url.split('/')[2]
            url = url[0:url.rfind("?")] + "/description"
            url = "https://www.kickstarter.com" + url
            title = unicode(title, "utf-8")
            url = unicode(url, "utf-8")
            item = [title,url]
            
            # filename is based on the unique string of the url
            filename = separater + '.csv'
            #print filename
            
            isafile = 0
            for file in filenames:
                if file == filename:
                    #print 'EXISTS in dir'
                    isafile = 1
            
            ## if it is a new file, write it into the ref to keep track of it
            if isafile == 0:
                print "does not EXIST in dir"
                csvWriter.writerow(item)
                
                ## impliment parser to go deeper to scrape details for new projects
                yield scrapy.Request(url, callback=self.parse_detail)
                
            
            ## opening the project file
            tf = open(rootdir+'/'+filename, 'ab')
            csvWriter2 = csv.writer(tf)
                
            current_date = time.strftime("%x")
            percent = project.xpath('div[3]/div[2]/ul/li[1]/div/text()').extract()[0].encode("ascii", "ignore")
            currency = project.xpath('div[3]/div[2]/ul/li[2]/div/span/@class').extract()[0].encode("ascii", "ignore")
            pledge = project.xpath('div[3]/div[2]/ul/li[2]/div/span/text()').extract()[0].encode("ascii", "ignore")
            end_date = project.xpath('div[3]/div[2]/ul/li[4]/@data-end_time').extract()[0].encode("ascii", "ignore")
            
            ## edit texts
            currency = currency.split(' ')[1]
            end_date = end_date.split('T')[0]
            
            percent = unicode(percent, "utf-8")
            currency = unicode(currency, "utf-8")
            pledge = unicode(pledge, "utf-8")
            end_date = unicode(end_date, "utf-8")
            
            ## array is 
            ## [current date, the percentage of fund, currency, pledge (goal), end date for the project]
            item2 = [current_date, percent, currency, pledge, end_date, url]
            ## print item2
            
            csvWriter2.writerow(item2)
            tf.close()
                
        
        f.close()
        
    ## scraping details for the project
    def parse_detail(self, response):
        ##print response.url
        sel = Selector(response)
        data = open('data.csv', 'ab')
        dataWriter = csv.writer(data)
        
        title = sel.xpath('//*[@id="content-wrap"]/section/div[1]/div/h2/a/text()').extract()[0].encode("ascii", "ignore")
        url = response.url
        backers = sel.xpath('//*[@id="backers_count"]/data/text()').extract()[0].encode("ascii", "ignore")
        fund = sel.xpath('//*[@id="pledged"]/data/text()').extract()[0].encode("ascii", "ignore")
        goal = sel.xpath('//*[@id="stats"]/div/div[2]/span/span[1]/text()').extract()[0].encode("ascii", "ignore")
        currency = sel.xpath('//*[@id="pledged"]/data/@data-currency').extract()[0].encode("ascii", "ignore")
        
        try:
            location = sel.xpath('//*[@id="content-wrap"]/section/div[2]/div/div[1]/div[2]/div[1]/div/a[1]/text()').extract()[0].encode("ascii", "ignore")
            location = location.replace("\n", " ")
        except:
            location = "N/A"
            
        try:
            tag = sel.xpath('//*[@id="content-wrap"]/section/div[2]/div/div[1]/div[2]/div[1]/div/a[2]/text()').extract()[0].encode("ascii", "ignore")
            tag = tag.replace("\n", " ")
        except:
            tag = "N/A"
            
        try:    
            company = sel.xpath('//*[@id="content-wrap"]/section/div[2]/div/div[2]/div[6]/div/div[2]/div[2]/h5/a/text()').extract()[0].encode("ascii", "ignore")
        except:
            company = "N/A"
            
        try:    
            end_date = sel.xpath('//*[@id="content-wrap"]/section/div[2]/div/div[2]/div[6]/div/div[1]/div/div/p/time/text()').extract()[0].encode("ascii", "ignore")
        except:
            end_date = "N/A"

        try:
            short_description = sel.xpath('//*[@id="content-wrap"]/section/div[2]/div/div[1]/div[2]/p/text()').extract()[0].encode("ascii", "ignore")
            short_description = short_description.replace("\n", " ")
        except:
            short_description = "N/A"
        
        title = unicode(title, "utf-8")
        backers = unicode(backers, "utf-8")
        fund = unicode(fund, "utf-8")
        goal = unicode(goal, "utf-8")
        currency = unicode(currency, "utf-8")
        location = unicode(location, "utf-8")
        tag = unicode(tag, "utf-8")
        company = unicode(company, "utf-8")
        end_date = unicode(end_date, "utf-8")
        short_description = unicode(short_description, "utf-8")
        
        item = [title, url, backers, fund, currency, goal, location, tag, company, end_date, short_description]
        dataWriter.writerow(item)
        data.close()
        
        