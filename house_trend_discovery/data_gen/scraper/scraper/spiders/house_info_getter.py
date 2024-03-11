from pathlib import Path
import re

import scrapy


class HouseInfoGetter(scrapy.Spider):
    name = "houseinfo"

    start_urls = [
        "https://www.snoco.org/proptax/search.aspx?address=23206%2056th%20Ave%20W"
    ]

    def parse(self, response):
        cell_texts = response.css("#mGrid td a::text").getall()
        parcel_number = cell_texts[0]

        base_url = response.url.replace("Results", "ParcelInfo")
        next_page = f"{base_url}?parcel_number={parcel_number}"

        def download_page(response):
            print(response.body)

        yield scrapy.Request(next_page, callback=download_page)

        #https://www.snoco.org/proptax/(S(z33tf4ucdwidxo5hnwettpie))/ParcelInfo.aspx?parcel_number=00586100200200
