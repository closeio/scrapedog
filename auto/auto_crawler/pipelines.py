# Define your item pipelines here
from scrapy.exceptions import DropItem
try:
    import json 
except ImportError:
    import simplejson as json

"""class NameNumberPipeline(object):

    def process_item(self, item, spider):
        return item
       
        if item['title'] or item['phone']:
            return item
        else: 
            raise DropItem("Missing title or number")
        """
