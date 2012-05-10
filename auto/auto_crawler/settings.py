# Scrapy settings for tutorial project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'AutoCrawler'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['auto_crawler.spiders']
NEWSPIDER_MODULE = 'auto_crawler.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = [] 
