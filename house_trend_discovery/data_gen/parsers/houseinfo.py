from bs4 import BeautifulSoup
from itertools import chain
import os
import re
from typing import List, Tuple
from house_trend_discovery.data_gen.models import PremiseDetails, County, LatLng
from house_trend_discovery.data_gen.parsers.parser import Parser as BaseParser, ScraperName, HomeScrapeResults
from house_trend_discovery.data_gen.parsers.utils import parse_table, combine_results, get_file, get_nums, parse_sideways_table
from house_trend_discovery.get_logger import get_logger

logger = get_logger(__name__)

"""
parses html for output from the houseinfo scrapy spider
"""
class Parser(BaseParser):
    def parse(self, output_file_paths: dict[ScraperName, List[HomeScrapeResults]]) -> List[PremiseDetails]:
        houseinfo_scrape_results = self._ingest_houseinfo_scrape_results(output_file_paths)
        return list(chain(*[self._build_scrape_result(r) for r in houseinfo_scrape_results]))

    def _build_scrape_result(self, raw: dict) -> List[PremiseDetails]:
        res = []
        try:
            market_values = raw["Market Total"]
            year_built = raw["Year Built"]
            years_assessed = raw["years_assessed"][1:]

            res = []
            for i in range(len(market_values)):
                try:
                    market_value = market_values[i]
                    year_assessed = years_assessed[i]

                    res.append(PremiseDetails(
                        assessment_urls = [l for l in [raw.get('url1'), raw.get('url2')] if l is not None],
                        premise_address = raw["address"],
                        parcel_number = raw["Parcel Number"][0],
                        year_assessed = year_assessed,
                        dollar_value = market_value,
                        year_built = year_built[0],
                        county = County(**raw['county']),
                        premise_location = LatLng(**raw['location'])
                    ))
                except Exception as e:
                    logger.error(f"Failed to build scrape result for index i = {i}", str(e))
        except Exception as e:
            logger.error(f"Failed to build scrape result: {e}")
        return res

    def _ingest_houseinfo_scrape_results(
            self, output_file_paths: dict[ScraperName, List[HomeScrapeResults]]) -> List[dict]:
        results = []

        for home_pages in output_file_paths['houseinfo']:
            res = {}
            for (page_number, url_path, page_path, inputs) in home_pages:
                res.update(inputs)
                if page_number == 1:
                    try:
                        res.update(parse_p1(url_path, page_path))
                    except Exception as e:
                        logger.error(f"Failed to parse page 1 for {url_path}", e)
                elif page_number == 2:
                    try:
                        res.update(parse_p2(url_path, page_path))
                    except Exception as e:
                        logger.error(f"Failed to parse page 2 for {url_path}", e)
            results.append(res)

        return results

def parse_p1(url_path: str, page_path: str):
    """
    parcel number and address
    """
    url = get_file(url_path)
    html = get_file(page_path)
    soup = BeautifulSoup(html, 'html.parser')

    return combine_results(parse_table(soup.find('table', id='mGrid')), {'url1':url})

def parse_p2(url_path: str, page_path: str):
    """
    gets property values
    """
    url = get_file(url_path)
    html = get_file(page_path)

    soup = BeautifulSoup(html, 'html.parser')
    property_value_headers = [t.get_text() for t in soup.find('table', id='mPropertyValues').find_all('th')]
    year_headers = [get_nums(t) for t in property_value_headers]

    property_values_table = parse_sideways_table(soup.find('table', id='mPropertyValues'))

    table_map = dict([(header, [get_nums(c) for c in cells]) for (header, cells) in property_values_table.items()])

    structures_table = parse_table(soup.find('table', id='mRealPropertyStructures'))

    return combine_results(table_map, structures_table, {'url2':url, 'years_assessed': year_headers})

def parse():
    p1 = parse_p1()
    p2 = parse_p2()
    logger.debug(p1)
    logger.debug(p2)

if __name__ == "__main__":
    print(Parser(scraper_name="houseinfo", data_base_path="./puppeteer_crawler/data").run().to_json())
