import click
import json
from typing import Optional, List
import importlib
from house_trend_discovery.data_gen.models import Location, PremiseScrapeResult, PremiseDetails

def build_db_rows(scraper_name: str) -> List[PremiseDetails]:
    # get scrape results
    # get inputs
    scrape_results = get_parser_results(scraper_name)
    scrape_inputs = get_scrape_inputs(scraper_name)

    street_addr_result_map = dict([(get_street_addr(r.premise_address).lower(), r) for r in scrape_results])
    street_addr_input_map = dict([(get_street_addr(r.address).lower(), r) for r in scrape_inputs])

    results = []
    for (key, location) in street_addr_input_map.items():
        result = street_addr_result_map.get(key)
        if result is not None:
            results.append(PremiseDetails(
                **dict(result),
                county=location.county,
                premise_location=location.location
            ))
        else:
            print(f"Couldn't find result for input {location}")
    return results

@click.command(help="Saves data from scraper into the database")
@click.option("--scraper_name", help="name of scraper", default=None)
def cli(scraper_name: Optional[str] = None):
    if scraper_name is not None:
        results = build_db_rows(scraper_name)
        # TODO send to a db
        print(results)

def get_street_addr(address: str) -> str:
    return address.split(",")[0]

def get_parser_results(scraper_name: str) -> List[PremiseScrapeResult]:
    mod = importlib.import_module(f"house_trend_discovery.data_gen.parsers.{scraper_name}")
    ParserClass = mod.Parser
    return ParserClass(scraper_name=scraper_name).run().get_results()

def get_scrape_inputs(scraper_name: str) -> List[Location]:
    path = f"house_trend_discovery/data_gen/scraper/inputs/{scraper_name}.json"
    with open(path, 'r') as f:
        return [Location(**l) for l in json.load(f)]
    return []

if __name__ == "__main__":
    cli()
