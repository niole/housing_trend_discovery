from typing import Union

from fastapi import FastAPI

app = FastAPI()

"""

Subscribe to news feeds. We look for certain kinds of news: new business establishing a headquarters, building
transportation, building entertainment, change in zoning laws, we could reach out to consumers of the API and ask
them what they would want to know about

get houses near a location in a year in a range of years

/homes?year_start=&year_end&address=&lat=&lng=&r=

Get a house's information
/homes/encoded_address?year_start=&year_end&r=

r - radius in miles
"""

@app.get("/homes")
def homes(year_start: Union[int, None] = None,
        year_end: Union[int, None] = None,
        address: Union[str, None] = None,
        lat: Union[str, None] = None,
        lng: Union[str, None] = None,
        r: Union[int, None] = None):
    print(locals().values())
    return []

@app.get("/homes/{address}")
def homes(address: str, year_start: Union[int, None] = None, year_end: Union[int, None] = None):
    print(locals().values())
    return []
