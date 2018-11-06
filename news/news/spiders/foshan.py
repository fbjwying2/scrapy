# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from news.items import NewsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import requests
import re
import json

def ListCombiner(lst):
    string = ''
    for e in lst:
        string += e
        #self.log('---------------------------------- %s' % (e))
    return string

def process_list_string(self, list_str):
    out_list = []
    for ttt in list_str:
        tt = ttt.strip().split('/r/n')
        for t in tt:
            sent = t.strip()
            if len(sent) > 0:
                self.log('---------------------------------- %s' % (sent))
                out_list.append(sent)
    return out_list

"""
class FoshanSpider(CrawlSpider):
    name = "foshan"
    allowed_domains = ["foshannews.com", "foshannews.net"]
    start_urls = ['http://www.foshannews.com/',
                  'http://www.foshannews.com/fstt/',
                  'http://www.foshannews.com/cc/',
                  'http://www.foshannews.com/nh/',
                  'http://www.foshannews.com/sd/',
                  'http://www.foshannews.com/gm/',
                  'http://www.foshannews.com/ss/',
                  'http://www.foshannews.com/jdyw/'
                  ]

    url_pattern = r'./*/t(\d{8})_(\d+)\.html'
    #url_pattern = r'./sd/sdtt/201810/t20181031_201924.html'
    #url_pattern = r'./index/fxfs/fsms/201810/t20181026_201033.html'
    #https://www.foshannews.net/jdyw/201810/t20181031_202106.html
    #url_pattern = r'./201810/t20181031_202106.html'


    rules = (
        Rule(LinkExtractor(allow=(url_pattern)), 'parse_news'),
    )

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        item = NewsItem()
        item['contents'] = {'link': str(response.url), 'title': u'', 'passage': u''}


        item['contents']['title'] = sel.xpath('////h1/text()').extract_first()

        list_doc = sel.xpath('//div[@class=\'cont\']/div/div/p/text()').extract()
        if len(list_doc) == 0:
            list_doc = sel.xpath('//div[@class=\'cont\']/div/div/div/text()').extract()

        item['contents']['passage'] = list_doc

        return item
"""


# 回归测试需要验证
# https://www.foshannews.net/jdyw/201810/t20181031_202106.html
# https://www.foshannews.net/kjzt2016/gdddh_26312/02016/201811/t20181106_203505.html
# https://www.foshannews.com/kjzt2016/gdddh_26312/02016/201811/t20181105_203179.html
# https://www.foshannews.net/jdyw/201811/t20181106_203382.html
# https://www.foshannews.net/jdyw/201810/t20181031_202109.html
# https://www.foshannews.net/jdyw/201811/t20181105_203219.html

class FoshanSpider(CrawlSpider):
    name = "foshan"
    allowed_domains = ["foshannews.com", "foshannews.net"]
    start_urls = [
        'http://www.foshannews.com/',
        'http://www.foshannews.com/fstt/',
        'http://www.foshannews.com/cc/',
        'http://www.foshannews.com/nh/',
        'http://www.foshannews.com/sd/',
        'http://www.foshannews.com/gm/',
        'http://www.foshannews.com/ss/',
        'http://www.foshannews.com/jdyw/',
        'http://www.foshannews.com/cc/sstt/',
        'http://www.foshannews.com/sd/sdtt/',
        'http://www.foshannews.com/nh/nhtt/',
        'http://www.foshannews.com/gm/gmtt/',
        'http://www.foshannews.com/ss/sstt/'
    ]

    url_pattern = r'./*/t(\d{8})_(\d+)\.html'

    rules = (
        Rule(LinkExtractor(allow=(url_pattern)), 'parse_news'),
    )

    page_link = set()
    def start_requests(self):

        self.page_link = {
            'http://www.foshannews.com/',
            'http://www.foshannews.com/fstt/',
            'http://www.foshannews.com/cc/',
            'http://www.foshannews.com/nh/',
            'http://www.foshannews.com/sd/',
            'http://www.foshannews.com/gm/',
            'http://www.foshannews.com/ss/',
            'http://www.foshannews.com/jdyw/'
        }

        # for local in ['jdyw']:
        for local in ['cc/cctt','sd/sdtt','nh/nhtt','gm/gmtt','ss/sstt', 'fstt', 'jdyw']:
            for i in range(1, 35):
                url = "http://www.foshannews.com/{}/index_{}.html".format(local, str(i))
                self.page_link.add(url)


        for url in self.page_link:
            yield self.make_requests_from_url(url)

    url_map = dict()
    def get_url_id(self, url):
        return url.split('/')[-1].split('.')[0]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))

        item = NewsItem()

        url_id = self.get_url_id(str(response.url))
        if url_id in self.url_map:
            self.url_map[url_id] += 1
            return item
        else:
            self.url_map[url_id] = 1

        item['contents'] = {'link': str(response.url), 'title': u'', 'passage': u''}
        item['contents']['title'] = sel.xpath('////h1/text()').extract_first()

        # 代码比较.........!)
        #list_doc = sel.xpath('//div[@class=\'cont\']/div/div/div/text()').extract()

        divs = sel.xpath('//div[@class=\'cont\']/div')

        list_doc = []
        for l in divs.xpath('.//div/text() | .//div/b/text()').extract():
            t = l.strip()
            if len(t) > 0:
                list_doc.append(t)

        for l in divs.xpath('.//span/text()').extract():
            t = l.strip()
            if len(t) > 0:
                list_doc.append(t)

        for l in divs.xpath('.//p/text() | .//p/strong/text()').extract():
            t = l.strip()
            if len(t) > 0:
                list_doc.append(t)

        item['contents']['passage'] = list_doc

        """
        list_doc = sel.xpath('//div[@class=\'cont\']/div/div/div/p/text()').extract()
        if len(list_doc) == 0:
            list_doc = sel.xpath('//div[@class=\'cont\']/div/div/div/text()').extract()
        """


        """
        divs = sel.xpath('//div[@class=\'cont\']/div/div/*')
        list_doc = divs.xpath('//span/text()').extract()
        list_doc = []
        for p in divs.xpath('//p/text()'):
            list_doc.append(p.extract())

        item['contents']['passage'] = list_doc
        """


        return item
