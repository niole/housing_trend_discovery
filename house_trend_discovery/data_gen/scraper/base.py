import json
from pathlib import Path
import os
import time
import re
import scrapy

class Base(scrapy.Spider):
    """
    You override
    """
    name = ""

    session_id = None

    """
    You override
    Input
        element from scraper input json  list

    Returns
        (key, url), where key identifies the house being scraped and will be used later to identify
        home entries in the database, and url which is the start url to begin scraping from
    """
    def create_start_url_pair(self, input_value) -> (str, str):
        return ("", "")

    """
    You override

    This is the first function that scrapy calls with the urls you provided it.

    **You must call self.init_dirs(key)**

    Input
        key: the key that identifies the home being scraped

    Response
        A scraper function that parses the response object from scrapy and saves the html file
        contents to the file system. The out path will be namespaced by the key
    """
    def parse(self, key):
        self.init_dirs(key)

        def block(response):
            # example
            self.write_out_path(
                key=key,
                pn=1,
                url=response.url,
                html=response.body.decode()
            )

        return block

    """
    Don't override

    Writes the found html files to the file system for parsing.

    Input
        key: the key that identifies the home being scraped
        pn: the page number, first page will be 1, etc...
        url: the url of the page
        html: the html contents of the page
    """
    def write_out_path(self, key: str, pn: int, url: str, html: str):
        session_id = self.get_session_id()

        with open(f"./data/{session_id}/{key}/page_{pn}.html", "w") as f:
            f.write(html)

        with open(f"./data/{session_id}/{key}/urls/url_{pn}.txt", "w") as f:
            f.write(url)

    def start_requests(self):
        urls = []
        with open(f"./inputs/{self.name}.json", "r") as f:
            inputs = json.load(f)
            urls = [self.create_start_url_pair(a) for a in inputs]

        for (key, url) in urls:
            yield scrapy.Request(url=url, callback=self.parse(key))


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
