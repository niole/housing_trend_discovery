from bs4 import BeautifulSoup
from typing import List, Tuple
from house_trend_discovery.data_gen.models import PremiseDetails, County, LatLng
from house_trend_discovery.data_gen.parsers.parser import Parser as BaseParser, ScraperName, HomeScrapeResults
from house_trend_discovery.data_gen.parsers.utils import parse_sideways_table, parse_table, get_nums
from house_trend_discovery.get_logger import get_logger

logger = get_logger(__name__)

class Parser(BaseParser):
    def parse(self, output_file_paths: dict[ScraperName, List[HomeScrapeResults]]) -> List[PremiseDetails]:
        king_county_result_paths = output_file_paths['kingcounty']

        return self._ingest_houseinfo_scrape_results(king_county_result_paths)

    def _ingest_houseinfo_scrape_results(self, paths: List[HomeScrapeResults]) -> List[PremiseDetails]:
        # each homescrapereults is the list of results for 1 home
        results = []

        for home_results in paths:
            # only 1 page is saved for kingcounty results
            (_, url_path, page_path, inputs) = home_results[0]
            url = None
            html = None
            with open(url_path, 'r') as f:
                url = f.read()

            with open(page_path, 'r') as f:
                html = f.read()

            if url is not None and html is not None:
                soup = BeautifulSoup(html, 'html.parser')

                parcel_table = parse_sideways_table(soup.find('table', id='cphContent_DetailsViewDashboardHeader'))

                logger.debug(f"parcel_table \n {parcel_table}")

                building_info_table = parse_sideways_table(soup.find('table', id='cphContent_DetailsViewPropTypeR'))

                logger.debug(f"building_info_table \n {building_info_table}")

                parcel_number = parcel_table['Parcel Number'][0]
                year_built = int(building_info_table['Year Built'][0])
                sq_feet = int(building_info_table['Total Square Footage'][0])
                bed_count = int(building_info_table['Number Of Bedrooms'][0])
                bath_count = float(building_info_table['Number Of Baths'][0])

                tax_roll_history_table = parse_table(soup.find('table', id='cphContent_GridViewDBTaxRoll'))

                logger.debug(f"tax_roll_history_table \n {tax_roll_history_table}")

                house_values = zip(tax_roll_history_table['Tax Year'], tax_roll_history_table['Appraised Total ($)'])

                for (str_year_assessed, str_dollar_value) in house_values:
                    year_assessed = int(str_year_assessed)
                    dollar_value = get_nums(str_dollar_value)
                    if year_assessed >= year_built:
                        res = PremiseDetails(
                            premise_address = inputs["address"],
                            assessment_urls=[url],
                            year_assessed=year_assessed,
                            dollar_value=dollar_value,
                            parcel_number=parcel_number,
                            sq_feet=sq_feet,
                            year_built=year_built,
                            bed_count=bed_count,
                            bath_count=bath_count,
                            county = County(**inputs['county']),
                            premise_location = LatLng(**inputs['location'])
                        )
                        results.append(res)
            else:
                logger.info(f"Skipping home {home_results[0]}, bc missing data")

        return results

if __name__ == "__main__":
    print(Parser(scraper_name="kingcounty", data_base_path="./puppeteer_crawler/data").run().to_json())
