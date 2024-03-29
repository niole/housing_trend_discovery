from abc import ABC, abstractmethod
import click
from glob import glob
import posixpath
import json
import os
import re
from itertools import groupby
from typing import List, Optional, Tuple, NewType, TypeAlias
from house_trend_discovery.data_gen.models import PremiseDetails
from house_trend_discovery.get_logger import get_logger

logger = get_logger(__name__)

"""
gets the pages for you and formats the output
you provide the parsers and the pages

Extend the parse method
"""

ScraperName = NewType("ScraperName", str)
PageNumber = NewType("PageNumber", int)
UrlPath = NewType("UrlPath", str)
PagePath = NewType("PagePath", str)
ScrapeInputs = NewType("ScrapeInputs", dict)
HomeScrapeResults: TypeAlias = List[Tuple[PageNumber, UrlPath, PagePath, ScrapeInputs]]

class Parser(ABC):
    session_id: Optional[str] = None
    scraper_name: Optional[str] = None
    results: List[PremiseDetails] = []

    data_base_path = "house_trend_discovery/data_gen/scraper/data"

    @abstractmethod
    def parse(self, output_file_paths: dict[str, List[Tuple[int, str, str]]]) -> List[PremiseDetails]:
        print('parser base class output file paths: \n', output_file_paths)
        return []


    def __init__(self,
            sid: Optional[str] = None,
            scraper_name: Optional[str] = None,
            data_base_path: Optional[str] = None):
        """
        if session id provided, parses specific session
        if scraper_name provided, parses the latest session for that parser
        """
        self.session_id = sid
        self.scraper_name = scraper_name
        self.data_base_path = data_base_path
        self.results = []

    def run(self):
        output_paths = self._get_scraper_output_file_paths()
        self.results = self.parse(output_paths)
        return self

    def to_json(self) -> str:
        return json.dumps([json.loads(r.model_dump_json()) for r in self.results])

    def get_results(self) -> List[PremiseDetails]:
        return self.results

    def _get_scraper_output_file_paths(self) -> dict[ScraperName, List[HomeScrapeResults]]:
        """
        Returns a mapping from scraper name to list (page number, url file path, page file path)

        Returns
            scraper_name -> [address_namespaced_scrape_results]
        """

        sessions = [d for d in self._get_session_dirs()]

        # group sessions by scraper name
        # [(scraper_name, [session_id])]
        session_groups = groupby(
            sorted([(get_scraper_name(d), posixpath.basename(d)) for d in sessions], key=lambda x: x[0]),
            lambda x: x[0]
        )
        sessions_outputs = [list(vs) for (_, vs) in session_groups]

        # [(scraper_name, session_id)]
        latest_unique_sessions = [self._get_recent_session_id(gs) for gs in sessions_outputs if len(gs) > 0]

        keyed_latest_session_paths: List[Tuple[ScraperName, List[HomeScrapeResults]]] = \
            [(session_key, self._get_home_scrape_results(sid)) for (session_key, sid) in latest_unique_sessions]

        return dict(keyed_latest_session_paths)

    def _get_recent_session_id(self, sessions_ids: List[Tuple[str, str]]) -> Tuple[str, str]:
        if len(sessions_ids) == 0:
            raise Exception("session_ids must not be empty to get recent session_id")

        p = r'.+-(\d+)$'
        sorted_ids = sorted([(s,  do_cap_match(p, s[1])) for s in sessions_ids], key=lambda x: x[1])

        return sorted_ids[-1][0]

    def _get_session_dirs(self) -> List[str]:
        if self.session_id:
            return glob(f"{self.data_base_path}/{self.session_id}")
        elif self.scraper_name:
            return glob(f"{self.data_base_path}/{self.scraper_name}*")
        else:
            return glob(f"{self.data_base_path}/*")

    def _get_home_scrape_results(self, session_id: str) -> List[HomeScrapeResults]:
        page_p = r'\/page_([0-9]+).html$'
        url_p = r'\/url_([0-9]+).txt$'

        home_scrape_results = []
        home_dirs = glob(f"{self.data_base_path}/{session_id}/*")
        for home_dir in home_dirs:

            # get inputs json if they exist
            inputs_json = None
            try:
                inputs_file_path = f"{home_dir}/inputs/inputs.json"
                with open(inputs_file_path, 'r') as f:
                    inputs_json = json.load(f)
            except Exception as e:
                logger.warn("Failed to get inputs", e)

            pages_path = f"{home_dir}/*.html"
            urls_path = f"{home_dir}/urls/*.txt"

            urls = glob(urls_path)
            pages = glob(pages_path)

            url_map = dict([(int(do_cap_match(url_p, p)), p) for p in urls])
            page_map = dict([(int(do_cap_match(page_p, p)), p) for p in pages])
            home_scrape_results.append([(i, url_map[i], page_map[i], inputs_json) for i in range(1, len(urls)+1)])

        return home_scrape_results

def do_cap_match(p, s) -> Optional[str]:
    m = re.search(p, s)
    if m is not None:
        return m.group(1)
    return None

def get_scraper_name(dirname: str) -> Optional[str]:
    p = r'\/(\w+)-.*$'
    return do_cap_match(p, dirname)


@click.command(
    help="Parses most recent data generated all scrapers, unless single session specified."
)
@click.option("--sid", help="The override session id", default=None)
@click.option("--name", help="The override scraper name", default=None)
def cli(sid: Optional[str], name: Optional[str]):
    p = Parser(sid, name)

    print(p.run())

if __name__ == "__main__":
    cli()
