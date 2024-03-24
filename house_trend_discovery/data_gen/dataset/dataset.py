import click
import json
from typing import Optional, List
import importlib
from house_trend_discovery.data_gen.models import PremiseDetails
from house_trend_discovery.get_logger import get_logger

logger = get_logger(__name__)

def get_parser_results(scraper_name: str, data_dir: str) -> List[PremiseDetails]:
    mod = importlib.import_module(f"house_trend_discovery.data_gen.parsers.{scraper_name}")
    ParserClass = mod.Parser
    return ParserClass(scraper_name=scraper_name, data_base_path=data_dir).run().get_results()

@click.command(help="Saves data from scraper into the database")
@click.option("--scraper_name", help="name of scraper", default=None)
@click.option("--data", help="Path to data directory", default="./puppeteer_crawler/data", type=click.Path(exists=True))
@click.option("--to_json", is_flag=True, help="Format the ouput as json", default=True)
@click.option("--out", help="Outpath for data", default=None, type=click.Path())
def cli(scraper_name: Optional[str], data: str, to_json: bool, out: str):
    if scraper_name is not None:
        results = get_parser_results(scraper_name, data)

        if to_json:
            results = json.dumps([json.loads(m.model_dump_json()) for m in results])

        if out:
            with open(out, 'w') as f:
                f.write(results)
        else:
            print(results)

if __name__ == "__main__":
    cli()
