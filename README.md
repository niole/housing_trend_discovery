# Data Processing
```sh
# generate addresses
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
- Define a json array inputs for the scraper in `house_trend_discovery/data_gen/scraper` that is named after your Scrapy scraper's `self.name`, i.e. `<name>.json`
- Define a parser in `house_trend_discovery/data_gen/parsers/` using `BeautifulSoup`

## Spider Definition and Output

Example

```python
# house_trend_discovery/data_gen/scraper/scraper/spiders/scrapername.py

from house_trend_discovery.data_gen.scraper import Base

class NewScraper(Base):
    name = "scrapername"

    def create_start_url_pair(self, home_id: str) -> (str, str):
        return (home_id, f"https://www.countywebiste.gov/{home_id}")

    def parse(self, key):
        # must call init dirs
        self.init_dirs(key)

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

## Parser Definition and Output

Example

TODO

```python
```
