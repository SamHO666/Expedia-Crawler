# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
import json
from scrapy.pipelines.images import ImagesPipeline


class ImageDownloaderPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item["itemType"] != "hotel":
            return item
        for image_url in item["image_urls"]:
            yield scrapy.Request("http://" + image_url[2:], meta={'imgType': "officialUpload", 'hotelId': item["hotelId"]})
        for i in range(len(item["reviews"])):
            for review_photo_url in item["reviews"][i]["commentPhotosUrls"]:
                yield scrapy.Request(review_photo_url, meta={'imgType': "userUpload", 'hotelId': item["hotelId"]})

    def item_completed(self, results, item, info):
        return item

    def file_path(self, request, response=None, info=None):
        imgType = request.meta["imgType"]
        hotelId = request.meta["hotelId"]
        image_guid = request.url.split('/')[-1]
        if imgType == "officialUpload":
            filename = 'crawledData/Beijing/HotelPhotos/{0}/officialUpload/{1}'.format(hotelId, image_guid)
        else:
            filename = 'crawledData/Beijing/HotelPhotos/{0}/userUpload/{1}'.format(hotelId, image_guid)
        return filename


class JsonWritePipeline(object):

    def __init__(self):
        self.summary = None
        self.hotelCollection = None
        self.hotelIndex = 0
        self.fileIndex = 0
        self.hotels = dict()
        self.hotelCollectionBaseName = "crawledData/Beijing/hotelCollection"

    def open_spider(self, spider):
        self.summary = open('crawledData/Beijing/summary.jl', 'w')
        self.hotelCollection = open(self.hotelCollectionBaseName + str(self.fileIndex) + ".jl", 'w')

    def close_spider(self, spider):
        self.summary.close()
        self.hotelCollection.write(json.dumps(self.hotels))
        self.hotelCollection.close()

    def process_item(self, item, spider):
        if item["itemType"] == "summary":
            line = json.dumps(dict(item)) + "\n"
            self.summary.write(line)
        if item["itemType"] == "hotel":
            if self.hotelIndex == 50:
                self.hotelCollection.write(json.dumps(self.hotels))
                self.hotelCollection.close()
                self.fileIndex += 1
                self.hotelCollection = open(self.hotelCollectionBaseName + str(self.fileIndex) + ".jl", 'w')
                self.hotelIndex = 0
                self.hotels = dict()
            self.hotels[self.hotelIndex] = dict(item)
            self.hotelIndex += 1
        return item
