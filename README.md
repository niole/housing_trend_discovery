# Data Processing
```sh
# generate addresses to run scraping on
# use these addresses as inputs to scrapers
poetry run python \
    house_trend_discovery/data_gen/gen_county_dataset.py  gen-addrs \
    --name "Mountlake Terrace, WA, USA" \
    --d 1
```

# County Webiste Scraping

House prices are tracked for free on county government websites. This establishes a plugin framework for writing scrapers
and html processors, which retrieve this data in a standardized way.

Do the following to support a new website.

- Define a spider in `house_trend_discovery/data_gen/scraper/scraper/spiders/` using `Scrapy`
- Define a json array inputs for the scraper in `house_trend_discovery/data_gen/scraper` that is named after your Scrapy scraper's `self.name`, i.e. `<name>.json`. Just use the output of `gen_county_dataset.py  gen-addrs`
- Define a parser in `house_trend_discovery/data_gen/parsers/` using `BeautifulSoup`

## Spider Definition and Output

Example

- generate scraper inputs
```sh
poetry run python \
    house_trend_discovery/data_gen/gen_county_dataset.py  gen-addrs \
    --name "Mountlake Terrace, WA, USA" \
    --d 1
    --out house_trend_discovery/data_gen/scraper/inputs/scrapername.json
```

- Define a spider for crawling
```python
# house_trend_discovery/data_gen/scraper/scraper/spiders/scrapername.py

from house_trend_discovery.data_gen.scraper import Base
from house_trend_discovery.data_gen.models import Location
from urllib.parse import quote

class NewScraper(Base):
    name = "scrapername"

    def create_start_url_pair(self, addr_json: dict) -> (str, str):
        location = Location(**location_json)
        home_id = quote(location.address)
        return (home_id, f"https://www.countywebiste.gov/{home_id}")

    def parse(self, key):
        def block(response):
            self.write_out_path(
                key=key,
                pn=1,
                url=response.url,
                html=response.body.decode()
            )

            parcel_number = response.css("#parcel_number").get()
            next_page = f"https://www.countywebiste.gov?parcel_number={parcel_number}"

            def download_page(response):
                self.write_out_path(
                    key=key,
                    pn=2,
                    url=response.url,
                    html=response.body.decode()
                )

            yield scrapy.Request(next_page, callback=download_page)

        return block
```

- run the spider
```sh
cd house_trend_discovery/data_gen/scraper
poetry run scrapy crawl scrapername
```

- Verify that the output was saved. The scraper saves 1 file for the url, and another file for the html page contents to the following dir structure:
```sh
house_trend_discovery/data_gen/scraper/data/
- {session_id}/ # determined by the scraper base, it's name and the date
    - {key}/ # determined by the scraper implementation, corresponds to an individual house
        - page_1.html
        - urls/
            - url_1.txt
```

- then define a parser to read the data into usable data structures

## Parser Definition and Output

- Example
```python
#house_trend_discovery/data_gen/parsers/scrapername.py
from house_trend_discovery.data_gen.parsers.parser import Parser, ScraperName, HomeScrapeResults
from bs4 import BeautifulSoup

class ScraperNameParser(Parser):
    def parse(self, output_file_paths: dict[ScraperName, List[HomeScrapeResults]]) -> List[PremiseScrapeResult]:
        houseinfo_scrape_results = self._ingest_houseinfo_scrape_results(output_file_paths)
        return list(chain(*[self._build_scrape_result(r) for r in houseinfo_scrape_results]))

    def _build_scrape_result(self, raw: dict) -> List[PremiseScrapeResult]:
        return PremiseScrapeResult(
            assessment_urls = [raw.get('url')],
            premise_address = raw["Location Address"],
            parcel_number = raw.get("Parcel Number"),
            year_assessed = raw["year_assessed"],
            dollar_value = raw["market_value"],
            year_built = raw["year_built"],
        )

    def _ingest_houseinfo_scrape_results(
            self, output_file_paths: dict[ScraperName, List[HomeScrapeResults]]) -> List[dict]:
        results = []

        for home_pages in output_file_paths['scrapername']:
            res = {}
            for (page_number, url_path, page_path) in home_pages:
                if page_number == 1:
                    res.update(parse_p1(url_path, page_path))
            results.append(res)

        return results

def parse_p1(url_path: str, page_path: str):
    url = get_file(url_path)
    html = get_file(page_path)
    soup = BeautifulSoup(html, 'html.parser')

    return combine_results(parse_table(soup.find('table', id='mGrid')), {'url':url})


if __name__ == "__main__":
    print(ScraperNameParser().run().to_json())
```

- run and read output
```sh
poetry run python house_trend_discovery/data_gen/parsers/scrapername.py | jq
```
