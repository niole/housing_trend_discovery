from pathlib import Path
import os
import time
from typing import Optional
from house_trend_discovery.data_gen import PremiseScrapeResult, County, LatLng
from urllib.parse import quote
import re
import scrapy


class HouseInfoGetter(scrapy.Spider):
    name = "houseinfo"

    start_urls = [
        "https://www.snoco.org/proptax/search.aspx?address=23206%2056th%20Ave%20W"
    ]

    def write_out_path(self, session_id: str, pn: int, url: str, html: str):
        with open(f"./data/{session_id}/page_{pn}.html", "w") as f:
            f.write(html)

        with open(f"./data/{session_id}/urls/url_{pn}.txt", "w") as f:
            f.write(url)

    def parse(self, response):
        session_id = f"{self.name}-{time.strftime('%H-%M-%S', time.gmtime())}"
        if not os.path.isdir('./data'):
            os.mkdir('./data')
        os.mkdir(f'./data/{session_id}')
        os.mkdir(f'./data/{session_id}/urls')
        self.write_out_path(session_id, 1, response.url, response.body.decode())

        cell_texts = response.css("#mGrid td a::text").getall()
        parcel_number = cell_texts[0]

        base_url = response.url.replace("Results", "ParcelInfo")
        next_page = f"{base_url}?parcel_number={parcel_number}"

        def download_page(response):
            self.write_out_path(session_id, 2, response.url, response.body.decode())

            # TODO can't get structure details, because can't get rsn or ext
            #structure_url = f"https://www.snoco.org/v1/propsys/PropInfo05-StructData.asp?parcel=00586100200200&lrsn=1146848&Ext=R01&StClass=Dwelling&Yr=1960&ImpId=D&ImpType=DWELL&StType=1%20Story%20w/Basement"
            #res = requests.get(next_page)
            #self.write_out_path(session_id, 3, res.text)

        yield scrapy.Request(next_page, callback=download_page)
