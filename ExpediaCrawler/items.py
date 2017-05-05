# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SummaryItem(scrapy.Item):
    itemType = scrapy.Field()
    totalCount = scrapy.Field()
    allHotelIds = scrapy.Field()
    allHotelCoords = scrapy.Field()


class HotelItem(scrapy.Item):
    itemType = scrapy.Field()

    # From Json Response
    hotelId = scrapy.Field()
    normalizedHotelName = scrapy.Field()
    cityName = scrapy.Field()
    neighborhood = scrapy.Field()
    structureType = scrapy.Field()
    hotelStarRating = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    infositeUrl = scrapy.Field()

    # From Source Code
    hotelDescription = scrapy.Field()
    hotelLocation = scrapy.Field()
    hotelFeature = scrapy.Field()
    roomAmenities = scrapy.Field()
    recommendPercentage = scrapy.Field()
    image_urls = scrapy.Field()

    # For Reviews Storage
    reviews = scrapy.Field()




