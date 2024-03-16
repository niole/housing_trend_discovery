from bs4 import BeautifulSoup
from itertools import chain
import json
import os
import re
from typing import List, Tuple
from house_trend_discovery.data_gen.models import PremiseScrapeResult, County, LatLng
from house_trend_discovery.data_gen.parsers.parser import Parser, ScraperName, HomeScrapeResults

"""
parses html for output from the houseinfo scrapy spider
"""
class HouseInfoParser(Parser):
    def parse(self, output_file_paths: dict[ScraperName, List[HomeScrapeResults]]) -> List[PremiseScrapeResult]:
        houseinfo_scrape_results = self._ingest_houseinfo_scrape_results(output_file_paths)
        return list(chain(*[self._build_scrape_result(r) for r in houseinfo_scrape_results]))

    def _build_scrape_result(self, raw: dict) -> List[PremiseScrapeResult]:
        # TODO get county, location from somewhere
        county = County(name="fake", state="fake"),
        premise_location = LatLng(lat=1, lng=1),
        market_values = raw["Market Total"]
        year_built = raw["Year Built"]
        years_assessed = raw["years_assessed"][1:]

        res = []
        for i in range(len(market_values)):
            market_value = market_values[i]
            year_assessed = years_assessed[i]
            res.append(PremiseScrapeResult(
                assessment_urls = [raw.get('url1'), raw.get('url2')],
                county = county,
                premise_location = premise_location,
                premise_address = raw["Location Address"],
                parcel_number = raw.get("Parcel Number"),
                year_assessed = year_assessed,
                dollar_value = market_value,
                year_built = year_built,
            ))
        return res

    def _ingest_houseinfo_scrape_results(
            self, output_file_paths: dict[ScraperName, List[HomeScrapeResults]]) -> List[dict]:
        results = []

        for home_pages in output_file_paths['houseinfo']:
            res = {}
            for (page_number, url_path, page_path) in home_pages:
                if page_number == 1:
                    res.update(parse_p1(url_path, page_path))
                elif page_number == 2:
                    res.update(parse_p2(url_path, page_path))
            results.append(res)

        return results

def get_nums(s):
    s = s.replace(',', '')
    m = re.search(r'(\d+)', s)
    if m is not None:
        return int(m.group(0))
    return None

def parse_p1(url_path: str, page_path: str):
    """
    parcel number and address
    """
    url = get_file(url_path)
    html = get_file(page_path)
    soup = BeautifulSoup(html, 'html.parser')

    return combine_results(parse_table(soup.find('table', id='mGrid')), {'url1':url, 'page1': html})

def parse_p2(url_path: str, page_path: str):
    """
    gets property values
    """
    url = get_file(url_path)
    html = get_file(page_path)

    soup = BeautifulSoup(html, 'html.parser')
    property_value_headers = [t.get_text() for t in soup.find('table', id='mPropertyValues').find_all('th')]
    year_headers = [get_nums(t) for t in property_value_headers]
    table_width = len(year_headers)

    cells = [t.get_text() for t in soup.find('table', id='mPropertyValues').find_all('td')]
    table_map = {}

    # parse sideways table
    for i in range(0, len(cells), table_width):
        header = cells[i]
        table_map[header] = [get_nums(t) for t in cells[i+1:i+table_width]]

    structures_table = parse_table(soup.find('table', id='mRealPropertyStructures'))

    return combine_results(table_map, structures_table, {'url2':url, 'page2': html, 'years_assessed': year_headers})

def combine_results(*argv) -> dict:
    res = {}
    for r in argv:
        res.update(r)
    return res

def parse_table(soup_table):
    headers = [t.get_text() for t in soup_table.find_all('th')]
    cells = [t.get_text() for t in soup_table.find_all('td')]
    return dict(zip(headers, cells))

def parse():
    p1 = parse_p1()
    p2 = parse_p2()
    print(p1)
    print(p2)

def get_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def no_nones(es: list) -> list:
    return [e for e in es if e is not None]

if __name__ == "__main__":
    res = HouseInfoParser(scraper_name="houseinfo").run()
    print(json.dumps([json.loads(r.model_dump_json()) for r in res]))