import click
import json
from typing import Optional, List
import importlib
from house_trend_discovery.data_gen.models import Location, PremiseScrapeResult, PremiseDetails

def build_db_rows(scraper_name: str, data_dir: str, inputs_dir: str) -> List[PremiseDetails]:
    # get scrape results
    # get inputs
    scrape_results = get_parser_results(scraper_name, data_dir)
    scrape_inputs = get_scrape_inputs(scraper_name, inputs_dir)

    street_addr_input_map = dict([(get_street_addr(r.address).lower(), r) for r in scrape_inputs])

    results = []
    for r in scrape_results:
        key = get_street_addr(r.premise_address).lower()
        location = street_addr_input_map.get(key)

        if location is not None:
            results.append(PremiseDetails(
                **dict(r),
                county=location.county,
                premise_location=location.location
            ))

    return results

@click.command(help="Saves data from scraper into the database")
@click.option("--scraper_name", help="name of scraper", default=None)
@click.option("--data", help="Path to data directory", default="./data", type=click.Path(exists=True))
@click.option("--inputs", help="Path to inputs directory", default="./inputs", type=click.Path(exists=True))
@click.option("--to_json", is_flag=True, help="Format the ouput as json", default=True)
@click.option("--out", help="Outpath for data", default=None, type=click.Path())
def cli(scraper_name: Optional[str], data: str, inputs: str, to_json: bool, out: str):
    if scraper_name is not None:
        results = build_db_rows(scraper_name, data, inputs)

        if to_json:
            results = json.dumps([json.loads(m.model_dump_json()) for m in results])

        if out:
            with open(out, 'w') as f:
                f.write(results)
        else:
            print(results)

def get_street_addr(address: str) -> str:
    return address.split(",")[0]

def get_parser_results(scraper_name: str, data_dir: str) -> List[PremiseScrapeResult]:
    mod = importlib.import_module(f"house_trend_discovery.data_gen.parsers.{scraper_name}")
    ParserClass = mod.Parser
    return ParserClass(scraper_name=scraper_name, data_base_path=data_dir).run().get_results()

def get_scrape_inputs(scraper_name: str, inputs_dir: str) -> List[Location]:
    path = f"{inputs_dir}/{scraper_name}.json"
    with open(path, 'r') as f:
        return [Location(**l) for l in json.load(f)]
    return []

if __name__ == "__main__":
    cli()
