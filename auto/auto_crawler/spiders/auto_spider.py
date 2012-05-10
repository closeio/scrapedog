from scrapy.spider import BaseSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from auto_crawler.items import AutoItem

import re

class PowerProfiles(BaseSpider):
    name = "auto"
    allowed_domains = ["powerprofiles.com"]
    start_urls = [
        "http://www.powerprofiles.com/profile/00005144184372/2-4D+FARMS%2C+INC-VEGA-TX-%28806%29+267-2865"
            ] 

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//div')
        items = [] 
        for site in sites:
           print sites 

