# County Website Scraping

House prices are tracked for free on county government websites. This establishes a plugin framework for writing scrapers
and html processors, which retrieve this data in a standardized way.

- generate address inputs, write a crawler to ingest those inputs, write a parser to parse the saved pages, all files are named the same: "scraper name"
- Put everything in their correct respective locations
- run the crawler: `cd puppeteer_crawler && node <scrapername>.js`
- Generate the data, by calling `house_trend_discovery/data_gen/dataset/dataset.py`

## Generate address inputs for crawler
```sh
# generate addresses to run scraping on
# use these addresses as inputs to scrapers
poetry run python \
    house_trend_discovery/data_gen/gen_county_dataset.py  gen-addrs \
    --name "Mountlake Terrace, WA, USA" \
    --d 1
    --out puppeteer_crawler/inputs/scrapername.json
```

## Define a crawler
```js
// puppeteer_crawler/scrapername.js
import puppeteer from 'puppeteer';
import Base from './base.js';

class HouseInfoCrawler extends Base {
    constructor(sessionId) {
        super(sessionId)
        this.name = "houseinfo";
    }

    parse(key, startUrl) {
        console.log("Crawling ", key, " ", startUrl);
        (async () => {
            const browser = await puppeteer.launch();
            const page = await browser.newPage();

            await page.goto(startUrl);

            const page1 = await this.getPageResults(page);
            await this.writeOutPath(key, 1, page1.url, page1.html);

            await browser.close();
        })();
    }

    createStartUrlPair(location) {
        const streetAddress = location.address;
        const encodedKey = encodeURI(streetAddress);
        return [
            encodedKey,
            "https://mysuperfake-website.com.gov"
        ];
    }
}

new HouseInfo().run()
```

- run the scrapername crawler
```sh
cd puppeteer_crawler
node scrapername.js
```

- Verify that the output was saved. The scraper saves 1 file for the url, and another file for the html page contents to the following dir structure:
```sh
puppeteer_crawler/data/
- {session_id}/ # determined by the scraper base, it's name and the date, scrapername-12347879
    - {key}/ # determined by the scraper implementation, corresponds to an individual house, encodedKey
        - page_1.html
        - inputs/ # the inputs for this house
            - inputs.json
        - screenshots/ # the scrapers save any screenshots in here
            - 1.png
        - urls/
            - url_1.txt
```

Then define a parser to read the data into usable data structures.

## Parser Definition and Output

- Example
```python
#house_trend_discovery/data_gen/parsers/scrapername.py
from typing import List, Tuple
from house_trend_discovery.data_gen.models import PremiseScrapeResult
from house_trend_discovery.data_gen.parsers.parser import Parser as ParserBase, ScraperName, HomeScrapeResults
from bs4 import BeautifulSoup

# parser must be named "Parser" to work with dataset.py script
class Parser(ParserBase):
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
    print(Parser(data_base_path="~/crawleroutputdir/").run().to_json())
```

- run and read output
```sh
poetry run python house_trend_discovery/data_gen/parsers/scrapername.py | jq
```

## Save Data to Dataset

Ingest data into the database.
```sh
poetry run python house_trend_discovery/data_gen/dataset/dataset.py --scraper_name scrapername
```

# TODO

## api server

- make server
- put data in DB
- support users
- api key issuing, expiration, rotation

## data generation

- location data generation is not distributed evenly throughout entire city
- sometimes, many of the generated addresses are not residential
- rename houseinfo to snohomish
- use constants to refer to scraper name in the code
- tests
