from bs4 import BeautifulSoup
import os
import re

"""
parses html for output from the houseinfo scrapy spider
"""

session_id = 'houseinfo-15-03-24'

def get_nums(s):
    s = s.replace(',', '')
    m = re.search(r'(\d+)', s)
    if m is not None:
        return int(m.group(0))
    return None

def parse_p1():
    """
    parcel number and address
    """
    page = "page_1.html"
    path = f"house_trend_discovery/data_gen/scraper/data/{session_id}/{page}"
    url = get_file(f"house_trend_discovery/data_gen/scraper/data/{session_id}/urls/url_1.txt")
    html = get_file(path)
    soup = BeautifulSoup(html, 'html.parser')

    return combine_results(parse_table(soup.find('table', id='mGrid')), {'url':url})

def parse_p2():
    """
    gets property values
    """
    page = "page_2.html"
    path = f"house_trend_discovery/data_gen/scraper/data/{session_id}/{page}"
    html = get_file(path)
    soup = BeautifulSoup(html, 'html.parser')
    url = get_file(f"house_trend_discovery/data_gen/scraper/data/{session_id}/urls/url_2.txt")
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

    return combine_results(table_map, structures_table, {'url':url})

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

if __name__ == "__main__":
    parse()
