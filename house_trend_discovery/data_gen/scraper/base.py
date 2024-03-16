from abc import ABC, abstractmethod
import json
from pathlib import Path
import os
import re
import scrapy
import time
from typing import Optional

class Base(scrapy.Spider, ABC):
    """
    You override
    """
    name = ""

    session_id = None

    """
    Input
        element from scraper input json  list

    Returns
        (key, url), where key identifies the house being scraped and will be used later to identify
        home entries in the database, and url which is the start url to begin scraping from
    """
    @abstractmethod
    def create_start_url_pair(self, input_value) -> (str, str, Optional[dict]):
        return ("", "", None)

    """
    This is the first function that scrapy calls with the urls you provided it.

    Input
        key: the key that identifies the home being scraped

    Response
        A scraper function that parses the response object from scrapy and saves the html file
        contents to the file system. The out path will be namespaced by the key
    """
    @abstractmethod
    def parse(self, key):
        def block(response):
            # example
            self.write_out_path(
                key=key,
                pn=1,
                url=response.url,
                html=response.body.decode(),
            )

        return block

    def run(self, key: str):
        self.init_dirs(key)
        return self.parse(key)

    """
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
            yield scrapy.Request(url=url, callback=self.run(key))


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
