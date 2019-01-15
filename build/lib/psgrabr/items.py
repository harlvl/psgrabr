# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyProjectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    nombreItem = scrapy.Field()
    precioBaseItem = scrapy.Field()
    nombreUsuarioComprador = scrapy.Field()
    sublist = scrapy.Field()
    externalLink = scrapy.Field()
    offerLink = scrapy.Field()
    offerPrice = scrapy.Field()
    message = scrapy.Field()
    timeAgo = scrapy.Field()
    pass
