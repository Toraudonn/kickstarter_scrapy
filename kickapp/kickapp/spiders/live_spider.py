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

## Parameters
TESTING = True

class LiveSpider(Spider):
    name = "LiveSpider"
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
        
        if TESTING is False:
            ## start scraping
            urls = ["https://www.kickstarter.com/discover/advanced?state=live&category_id=16&sort=newest&seed=2444597&page=%d" %(n) for n in range (1,end_page+1)]
            for url in urls:
                ## when dont_filter is false, it filters page=1 
                yield scrapy.Request(url, callback=self.parse, dont_filter = True)
        else:
            ## for test purposes (only one page scraping)
            yield scrapy.Request("https://www.kickstarter.com/discover/advanced?state=live&category_id=16&sort=newest&seed=2444597&page=1", callback= self.parse, dont_filter = True)
            
    ## goes through the list page
    def parse(self, response):
        #print response.url
        ## setting up the rootdir of the projects files
        ##============================================================================##
        rootdir = os.environ['PWD'] + '/projects'
        ##============================================================================##
        filenames = os.listdir(rootdir)
        
        sel = Selector(response)
        projects = sel.xpath('//*[@id="projects_list"]/*/*/div')
        
        for project in projects:
            url = project.xpath('div[2]/h6/a/@href').extract()[0].encode("ascii", "ignore")
            separater = url.split('/')[2]
            url = url[0:url.rfind("?")] + "/description"
            url = "https://www.kickstarter.com" + url
            url = unicode(url, "utf-8")
            
            ## filename is based on the unique string of the url
            filename = separater + '.csv'
            
            ## checks to see if it's already traking the project
            isafile = 0
            for file in filenames:
                if file == filename:
                    isafile = 1
            
            if isafile == 0:
                print "does not EXIST in dir"
                ## impliment google sheets api to save new projects here:
                self.save_to_sheet(url)
                
                ## impliment parser to go deeper to scrape details for new projects
                if TESTING is False:
                    yield scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
                
                
            ## scrapes daily
            if TESTING is False:
                yield scrapy.Request(url, callback=self.parse_data, dont_filter=True)
            
    
    ## scraping data for the project        
    def parse_data(self, response):
        sel = Selector(response)
        separater = sel.xpath('//*[@id="content-wrap"]/section/div[1]/div/h2/a/@href').extract()[0].encode("ascii", "ignore").split('/')[2]
        ##============================================================================##
        rootdir = os.environ['PWD'] + '/projects/'
        ##============================================================================##
        filename = separater + '.csv'
        f = open(rootdir+filename, 'ab')
        csvWriter = csv.writer(f)
        ## details
        current_date = time.strftime("%x")
        url = response.url
        backers = str(sel.xpath('//*[@id="backers_count"]/data/@data-value').extract()[0].encode("ascii", "ignore"))
        try:
            backers = backers.replace(",","")
        finally:
            backers = float(backers)
        currency = str(sel.xpath('//*[@id="pledged"]/data/@data-currency').extract()[0].encode("ascii", "ignore"))
        currency = currency.lower()
        fund = float(sel.xpath('//*[@id="pledged"]/data/@data-value').extract()[0].encode("ascii", "ignore"))
        ## initialize it to dollars
        fund_in_dollars = fund
        percent = float(sel.xpath('//*[@id="pledged"]/@data-percent-raised').extract()[0].encode("ascii", "ignore"))
        ## change fund into usd (if it does not recognize the currency, it will not change the currency)
        rate = 1.0
        if currency != 'usd':
            ##============================================================================##
            rootdir = os.environ['PWD'] + '/rates'
            ##============================================================================##
            filenames = os.listdir(rootdir)
            for file in filenames:
                if file == currency+'.csv':
                    with open(rootdir+'/'+file, 'rb') as csvfile:
                        csvReader = csv.reader(csvfile)
                        rows = list(csvReader)
                        rate = float(rows[0][0])
                        fund_in_dollars = fund * rate
        ## rewards 
        reward_backers = []
        try:
            rewards = sel.xpath('//*[@id="content-wrap"]/div[2]/section[1]/div/div/div/div/div[2]/div[1]/div/ol/li[*]')
            for reward in rewards:
                some_number = str(reward.xpath('div[2]/div[3]/span[last()]/text()').extract()[0].encode("ascii","ignore")).split(' ')[0]
                try:
                    some_number = some_number.replace(",", "")
                finally:
                    try:
                        some_number = float(some_number)
                    except:
                        some_number = float(-1.0)
                    reward_backers.append(some_number)                                                                                                                                   
        except:
            reward_backers = []
        
        ## change utf code type for saving
        current_date = unicode(current_date, "utf-8")
        url = unicode(url, "utf-8")
        currency = unicode(currency, "utf-8")
            
        item = [current_date, backers, currency, fund, fund_in_dollars, percent, rate, reward_backers, url]
        csvWriter.writerow(item)
        f.close()
        
        
    ## scraping details for the project
    def parse_detail(self, response):
        ##print response.url
        sel = Selector(response)
        rootdir = os.environ['PWD']
        data = open(rootdir+'/data.csv', 'ab')
        dataWriter = csv.writer(data)
        
        title = sel.xpath('//*[@id="content-wrap"]/section/div[1]/div/h2/a/text()').extract()[0].encode("ascii", "ignore")
        url = response.url
        backers = str(sel.xpath('//*[@id="backers_count"]/data/@data-value').extract()[0].encode("ascii", "ignore"))
        try:
            backers = backers.replace(",","")
        finally:
            backers = float(backers)
        fund = float(sel.xpath('//*[@id="pledged"]/data/@data-value').extract()[0].encode("ascii", "ignore"))
        goal = float(sel.xpath('//*[@id="pledged"]/@data-goal').extract()[0].encode("ascii", "ignore"))
        currency = str(sel.xpath('//*[@id="pledged"]/data/@data-currency').extract()[0].encode("ascii", "ignore")).lower()
        
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
        
        ## rewards
        reward_list = []
        try:
            rewards = sel.xpath('//*[@id="content-wrap"]/div[2]/section[1]/div/div/div/div/div[2]/div[1]/div/ol/li[*]')
            for reward in rewards:
                reward_detail = []
                try:
                    reward_detail.append(unicode(str(reward.xpath('div[2]/h3[@class="pledge__title"]/text()').extract()[0].encode("ascii","ignore")).replace("\n",""), "utf-8"))
                except:
                    reward_detail.append(unicode(str("No Title"),"utf-8"))
                some_number = str(reward.xpath('div[2]/h2/span[@class="pledge__currency-conversion"]/span/text()').extract()[0].encode("ascii","ignore")).split(' ')[0].split('$')[1]
                try:
                    # get rid of ',' notation for numbers such as '$1,000'
                    some_number = some_number.replace(",", "")
                finally:
                    # the reward currency is "USD"
                    try:
                        some_number = float(some_number)
                    except:
                        some_number = float(-1.0)
                    reward_detail.append(some_number)
                reward_list.append(reward_detail)
        except:
            reward_list = []
        
        ## change utf code for saving          
        title = unicode(title, "utf-8")
        currency = unicode(currency, "utf-8")
        location = unicode(location, "utf-8")
        tag = unicode(tag, "utf-8")
        company = unicode(company, "utf-8")
        end_date = unicode(end_date, "utf-8")
        short_description = unicode(short_description, "utf-8")
        
        item = [title, url, backers, fund, currency, goal, location, tag, company, end_date, short_description, reward_list]
        dataWriter.writerow(item)
        data.close()
        
        
    def save_to_sheet(self,url):
        print "saving (%s)to sheet..." %url
        
        ## API of google sheets:
        
        
        print "done!"