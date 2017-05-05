import scrapy
import json
from ExpediaCrawler.items import SummaryItem
from ExpediaCrawler.items import HotelItem


class ExpediaSpider(scrapy.Spider):
    name = "ExpediaSpider"
    startDate = "10/03/2018"
    endDate = "11/03/2018"
    regionId = "178237"
    destination = "Beijing+(and+vicinity),+China"
    url = "https://www.expedia.com.au/Hotel-Search-Data?responsive=true"
    body = "destination=" + destination + "&startDate=" + startDate + "&endDate=" + endDate + "&adults=2&regionId" \
           "=" + regionId + "&inventory=regular&sort=price&langid=3081&hashParam=undefined&hsrIdentifier=HSR&timezoneOffset" \
           "=36000000"
    headers = {
        'content-type': "application/x-www-form-urlencoded"
    }

    def start_requests(self):
        urls = [
            self.url
        ]

        for url in urls:
            yield scrapy.Request(url=url,
                                 method="POST",
                                 body=self.body,
                                 headers=self.headers,
                                 callback=self.parse)

    def parse(self, response):
        print("Succeed with Json response")
        ResponseDict = json.loads(response.body.decode("utf-8"))

        # Process result
        # 在第一页获取总结信息，包括所有酒店数目，id，经纬度等
        if ResponseDict["pagination"]["isFirstPage"]:
            summary = SummaryItem(itemType="summary")
            summary["totalCount"] = ResponseDict["pagination"]["totalCount"]
            summary["allHotelIds"] = ResponseDict["searchResults"]["allHotelIds"]
            summary["allHotelCoords"] = ResponseDict["searchResults"]["allHotelCoords"]
            yield summary

        # 处理每一页的具体酒店信息，每一页50条
        results = ResponseDict["results"]

        for i in range(len(results)):
            hotel = HotelItem(itemType="hotel")
            # 解析Json里面酒店的信息
            retailHotelInfoModel = results[i].get("retailHotelInfoModel")
            if retailHotelInfoModel is None:
                continue
            hotel["hotelId"] = retailHotelInfoModel.get("hotelId")
            hotel["normalizedHotelName"] = retailHotelInfoModel.get("normalizedHotelName")
            hotel["cityName"] = retailHotelInfoModel.get("cityName")
            hotel["neighborhood"] = retailHotelInfoModel.get("neighborhood")
            hotel["structureType"] = retailHotelInfoModel.get("structureType")
            hotel["hotelStarRating"] = retailHotelInfoModel.get("hotelStarRating")
            hotel["latitude"] = retailHotelInfoModel.get("latitude")
            hotel["longitude"] = retailHotelInfoModel.get("longitude")
            hotel["infositeUrl"] = results[i].get("infositeUrl")

            hotelPageRequest = scrapy.Request(hotel["infositeUrl"], callback=self.hotel_parse)
            hotelPageRequest.meta['hotel'] = hotel

            yield hotelPageRequest

        # 获取下一页50条的内容
        if not ResponseDict["pagination"]["isLastPage"]:
            PageNumber = str(int(ResponseDict["pagination"]["pageNumber"]) + 1)
            NextPageBody = self.body + "&page=" + PageNumber
            yield scrapy.Request(url=self.url,
                                 method="POST",
                                 body=NextPageBody,
                                 headers=self.headers,
                                 callback=self.parse)

    def hotel_parse(self, response):
        hotel = response.meta['hotel']
        # 解析页面源码里酒店的信息
        # 所有酒店图片地址
        try:
            hotel["image_urls"] = response.xpath("//img[@data-index]/@data-src").extract()
            hotel["recommendPercentage"] = response.xpath("//span[@class='recommend-percentage']/text()").extract()[0][:3]
        except IndexError:
            hotel["recommendPercentage"] = ""

        try:
            hotel["hotelDescription"] = response.xpath("//div[@class='hotel-description']/h2/text()").extract()[0]
        except IndexError:
            hotel["hotelDescription"] = ""

        try:
            generalDescription = response.xpath("//div[@class='hotel-description']//p/text()").extract()
            hotel["hotelLocation"] = generalDescription[0]
            hotel["hotelFeature"] = generalDescription[1]
            hotel["roomAmenities"] = generalDescription[2]
        except IndexError:
            hotel["hotelLocation"] = ""
            hotel["hotelFeature"] = ""
            hotel["roomAmenities"] = ""

        # 获取评论，设置评论条数为100000000则返回全部评论
        reviewsUrl = "https://www.expedia.com.au/ugc/urs/api/hotelreviews/hotel/" + hotel["hotelId"] + "/?_type=json&start=0&items=100000000&sortBy=DATEDESC"
        reviewRequest = scrapy.Request(url=reviewsUrl, callback=self.review_parse)
        reviewRequest.meta['hotel'] = hotel
        yield reviewRequest

    def review_parse(self, response):
        hotel = response.meta['hotel']
        ResponseDict = json.loads(response.body.decode("utf-8"))
        ResponseReviews = ResponseDict["reviewDetails"]["reviewCollection"]["review"]
        reviews = {}
        for i in range(len(ResponseReviews)):
            review = dict()
            review["reviewSubmissionTime"] = ResponseReviews[i]["reviewSubmissionTime"]
            review["title"] = ResponseReviews[i]["title"]
            review["reviewText"] = ResponseReviews[i]["reviewText"]
            review["positiveRemarks"] = ResponseReviews[i]["positiveRemarks"]
            review["negativeRemarks"] = ResponseReviews[i]["negativeRemarks"]
            review["locationRemarks"] = ResponseReviews[i]["locationRemarks"]
            review["ratingOverall"] = ResponseReviews[i]["ratingOverall"]
            review["ratingRoomCleanliness"] = ResponseReviews[i]["ratingRoomCleanliness"]
            review["ratingHotelCondition"] = ResponseReviews[i]["ratingHotelCondition"]
            review["ratingService"] = ResponseReviews[i]["ratingService"]
            review["ratingRoomComfort"] = ResponseReviews[i]["ratingRoomComfort"]
            review["userLocation"] = ResponseReviews[i]["userLocation"]
            review["managementResponses"] = {}
            for k in range(len(ResponseReviews[i]["managementResponses"])):
                managementResponse = dict()
                managementResponse["response"] = ResponseReviews[i]["managementResponses"][k]["response"]
                managementResponse["date"] = ResponseReviews[i]["managementResponses"][k]["date"]
                review["managementResponses"][k] = managementResponse
            review["commentPhotosUrls"] = []
            for j in range(len(ResponseReviews[i]["photos"])):
                review["commentPhotosUrls"].append(ResponseReviews[i]["photos"][j]["normalUrl"].split("?")[0])
            reviews[i] = review
        hotel["reviews"] = reviews
        yield hotel











