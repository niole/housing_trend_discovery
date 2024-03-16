import scrapy
from urllib.parse import quote
from typing import Optional
from house_trend_discovery.data_gen.scraper.base import Base
from house_trend_discovery.data_gen.models import Location

class HouseInfoGetter(Base):
    name = "houseinfo"

    def create_start_url_pair(self, location_json: dict) -> (str, str):
        location = Location(**location_json)
        address = location.address.split(",")[0]
        encoded_addr = quote(address)
        return (
            encoded_addr,
            f"https://www.snoco.org/proptax/search.aspx?address={encoded_addr}"
        )

    def parse(self, key):
        def block(response):
            self.write_out_path(
                key=key,
                pn=1,
                url=response.url,
                html=response.body.decode()
            )

            cell_texts = response.css("#mGrid td a::text").getall()
            parcel_number = cell_texts[0]

            base_url = response.url.replace("Results", "ParcelInfo")
            next_page = f"{base_url}?parcel_number={parcel_number}"

            def download_page(response):
                self.write_out_path(
                    key=key,
                    pn=2,
                    url=response.url,
                    html=response.body.decode()
                )

                # TODO can't get structure details, because can't get rsn or ext
                #structure_url = f"https://www.snoco.org/v1/propsys/PropInfo05-StructData.asp?parcel=00586100200200&lrsn=1146848&Ext=R01&StClass=Dwelling&Yr=1960&ImpId=D&ImpType=DWELL&StType=1%20Story%20w/Basement"
                return None

            yield scrapy.Request(next_page, callback=download_page)

        return  block
