import click
from glob import glob
import os
import re
from itertools import groupby
from typing import List, Optional, Tuple
from house_trend_discovery.data_gen.models import PremiseScrapeResult

"""
gets the pages for you and formats the output
you provide the parsers and the pages
"""

class Parser:
    session_id: Optional[str] = None

    data_base_path = "house_trend_discovery/data_gen/scraper/data"

    def __init__(self, sid: Optional[str] = None):
        self.session_id = sid

    def parse(self) -> List[PremiseScrapeResult]:
        self._list_pages()
        return []

    def _list_pages(self):
        # gets (url, page) paths for unique scrape sessions for latest of each
        #path = f"house_trend_discovery/data_gen/scraper/data/{session_id}/{page}"

        def do_cap_match(p, s) -> Optional[str]:
            m = re.search(p, s)
            if m is not None:
                return m.group(1)
            return None

        def get_scraper_name(dirname: str) -> Optional[str]:
            p = r'^(\w+)'
            return do_cap_match(p, dirname)

        def get_url_page(session_id: str) -> List[Tuple[str, str]]:
            page_p = r'\/page_([0-9]+).html$'
            url_p = r'\/url_([0-9]+).txt$'

            pages_path = f"{self.data_base_path}/{session_id}/*.html"
            urls_path = f"{self.data_base_path}/{session_id}/urls/*.txt"
            urls = glob(urls_path)
            pages = glob(pages_path)

            url_map = dict([(int(do_cap_match(url_p, p)), p) for p in urls])
            page_map = dict([(int(do_cap_match(page_p, p)), p) for p in pages])

            return [(url_map[i], page_map[i]) for i in range(1, len(urls)+1)]

        sessions = [d for d in os.listdir(self.data_base_path)]
        session_groups = groupby(
            sorted([(get_scraper_name(d), d) for d in sessions], key=lambda x: x[0]),
            lambda x: x[0]
        )
        sessions_groups_lists = [(k, list(vs)) for (k, vs) in session_groups]
        latest_unique_sessions = [sorted(gs)[-1] for (_, gs) in sessions_groups_lists if len(gs) > 0]

        keyed_latest_session_paths: Tuple[str, List[Tuple[str, str]]] = \
            [(session_key, get_url_page(sid)) for (session_key, sid) in latest_unique_sessions]
        print(keyed_latest_session_paths)

        # TODO call the right parser and pass url and page paths to them
        return keyed_latest_session_paths


@click.command(
    help="Parses most recent data generated all scrapers, unless single session specified."
)
@click.option("--sid", help="The override session id", default=None)
def cli(sid: Optional[str]):
    p = Parser(sid)

    print(p.parse())

if __name__ == "__main__":
    cli()
