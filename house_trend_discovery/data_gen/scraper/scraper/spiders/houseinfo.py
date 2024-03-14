import json
from pathlib import Path
import os
import time
import re
import scrapy
from typing import Optional
from urllib.parse import quote
from house_trend_discovery.data_gen import PremiseScrapeResult, County, LatLng


class HouseInfoGetter(scrapy.Spider):
    name = "houseinfo"
    session_id = None

    def start_requests(self):
        def create_start_url_pair(address: str) -> str:
            encoded_addr = quote(address)
            return (encoded_addr, f"https://www.snoco.org/proptax/search.aspx?address={encoded_addr}")

        urls = []
        with open(f"./inputs/{self.name}.json", "r") as f:
            addresses = json.load(f)
            urls = [create_start_url_pair(a) for a in addresses]

        for (key, url) in urls:
            yield scrapy.Request(url=url, callback=self.parse(key))

    def write_out_path(self, key: str, pn: int, url: str, html: str):
        session_id = self.get_session_id()

        with open(f"./data/{session_id}/{key}/page_{pn}.html", "w") as f:
            f.write(html)

        with open(f"./data/{session_id}/{key}/urls/url_{pn}.txt", "w") as f:
            f.write(url)

    def get_session_id(self) -> str:
        if self.session_id is None:
            self.session_id = f"{self.name}-{time.strftime('%H-%M-%S', time.gmtime())}"
        return self.session_id

    def init_dirs(self, key: str):
        def safe_mkdir(path):
            if not os.path.isdir(path):
                os.mkdir(path)
        session_id = self.get_session_id()

        safe_mkdir('./data')
        safe_mkdir(f'./data/{session_id}')
        safe_mkdir(f'./data/{session_id}/{key}')
        safe_mkdir(f'./data/{session_id}/{key}/urls')

    def parse(self, key):
        self.init_dirs(key)

        def block(response):
            self.write_out_path(
                key=key,
                pn=1,
                url=response.url,
                html=response.body.decode()
            )

            cell_texts = response.css("#mGrid td a::text").getall()
            parcel_number = cell_texts[0]

            base_url = response.url.replace("Results", "ParcelInfo")
            next_page = f"{base_url}?parcel_number={parcel_number}"

            def download_page(response):
                self.write_out_path(
                    key=key,
                    pn=2,
                    url=response.url,
                    html=response.body.decode()
                )

                # TODO can't get structure details, because can't get rsn or ext
                #structure_url = f"https://www.snoco.org/v1/propsys/PropInfo05-StructData.asp?parcel=00586100200200&lrsn=1146848&Ext=R01&StClass=Dwelling&Yr=1960&ImpId=D&ImpType=DWELL&StType=1%20Story%20w/Basement"
                #res = requests.get(next_page)
                #self.write_out_path(session_id, 3, res.text)

            yield scrapy.Request(next_page, callback=download_page)

        return block
