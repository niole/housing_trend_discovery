from bs4 import BeautifulSoup
from itertools import chain
import os
import re
from typing import List, Tuple
from house_trend_discovery.data_gen.models import PremiseScrapeResult
from house_trend_discovery.data_gen.parsers.parser import Parser as BaseParser, ScraperName, HomeScrapeResults

"""
parses html for output from the houseinfo scrapy spider
"""
class Parser(BaseParser):
    def parse(self, output_file_paths: dict[ScraperName, List[HomeScrapeResults]]) -> List[PremiseScrapeResult]:
        houseinfo_scrape_results = self._ingest_houseinfo_scrape_results(output_file_paths)
        return list(chain(*[self._build_scrape_result(r) for r in houseinfo_scrape_results]))

    def _build_scrape_result(self, raw: dict) -> List[PremiseScrapeResult]:
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
                    res.append(PremiseScrapeResult(
                        assessment_urls = [raw.get('url1'), raw.get('url2')],
                        premise_address = raw["Location Address"],
                        parcel_number = raw.get("Parcel Number"),
                        year_assessed = year_assessed,
                        dollar_value = market_value,
                        year_built = year_built,
                    ))
                except Exception as e:
                    print(f"Failed to build scrape result for index i = {i} of {raw}: {e}")
        except Exception as e:
            print(f"Failed to build scrape result for {raw}: {e}")
        return res

    def _ingest_houseinfo_scrape_results(
            self, output_file_paths: dict[ScraperName, List[HomeScrapeResults]]) -> List[dict]:
        results = []

        for home_pages in output_file_paths['houseinfo']:
            res = {}
            for (page_number, url_path, page_path) in home_pages:
                if page_number == 1:
                    try:
                        res.update(parse_p1(url_path, page_path))
                    except Exception as e:
                        print(f"Failed to parse page 1 for {url_path}: {e}")
                elif page_number == 2:
                    try:
                        res.update(parse_p2(url_path, page_path))
                    except Exception as e:
                        print(f"Failed to parse page 2 for {url_path}: {e}")
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
    print(Parser(scraper_name="houseinfo").run().to_json())
