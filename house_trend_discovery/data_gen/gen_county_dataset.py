import click
import googlemaps
import itertools
import json
from latloncalc.latlon import LatLon, Latitude, Longitude
import os
from models import Area, LatLng, Location, County
from dotenv import load_dotenv
load_dotenv()

gmaps = googlemaps.Client(key=os.environ['GOOGLE_CLOUD_API_KEY'])

def get_address_from_lat_lng(latlng):
    addresses = gmaps.reverse_geocode(latlng.to_string())
    if len(addresses) > 0:
        return addresses[0]
    return None

def get_county(a):
    county_index = next((i for i in range(len(a['address_components'])) if 'County' in a['address_components'][i]['long_name']), None)
    county_name = ''
    state_name = ''

    if county_index is not None:
        county_name = a['address_components'][county_index]['long_name']
        if county_index+1 < len(a['address_components']):
            state_name = a['address_components'][county_index+1]['long_name']

    return County(name=county_name, state=state_name)

def create_location_result(a):
    county = get_county(a)
    return Location(
        address=a['formatted_address'],
        county=county,
        location=LatLng(
            lat=a['geometry']['location']['lat'],
            lng=a['geometry']['location']['lng']
        )
    )

"""
Use geocoding API to get lat lng data about town, also returns county data
https://developers.google.com/maps/documentation/geocoding/requests-geocoding#geocoding-lookup

returns the lat lng of the boundary and the center
"""
def get_location_data(name: str) -> list[Area]:
    locations = gmaps.geocode(name)
    results = [create_area_result(name, l) for l in locations]
    return results

def create_area_result(query, l):
    county = get_county(l)
    geo = l['geometry']
    ne_bound = geo['bounds']['northeast']
    sw_bound = geo['bounds']['southwest']
    return Area(
        query=query,
        address=l['formatted_address'],
        county=county,
        ne_bound=LatLng(lat=ne_bound['lat'],lng=ne_bound['lng']),
        sw_bound=LatLng(lat=sw_bound['lat'],lng=sw_bound['lng']),
        location=LatLng(lat=geo['location']['lat'],lng=geo['location']['lng'])
    )

"""
This generates a house price dataset for a lat lng boundary
at D increments, retrieves addresses via the google maps reverse geocoding API
"""
def get_addresses(d, area):
    def select_coords_in_heading(d, start, finish):
        # generates coorindates until current coordinate >= finish
        # generates coords until step is longer than start to finish
        curr = start
        max_distance = start.distance(finish)
        coords = []
        while start.distance(curr) < max_distance:
            if curr != start and curr != finish:
                coords.append(curr)

            curr = curr.offset(curr.heading_initial(finish), d*1.6)

        return coords

    def generate_lat_lngs(d, area):
        # from center coord, generate in d increments until >= the coords below..
        ne = LatLon(area.ne_bound.lat, area.ne_bound.lng)
        nw = LatLon(area.ne_bound.lat, area.sw_bound.lng)
        sw = LatLon(area.sw_bound.lat, area.sw_bound.lng)
        se = LatLon(area.sw_bound.lat, area.ne_bound.lng)


        ew_mid_point_dist = ne.distance(nw)/2.0
        ns_mid_point_dist = ne.distance(se)/2.0

        north = ne.offset(ne.heading_initial(nw), ew_mid_point_dist)
        south = se.offset(se.heading_initial(sw), ew_mid_point_dist)
        east = se.offset(se.heading_initial(ne), ns_mid_point_dist)
        west = sw.offset(sw.heading_initial(nw), ns_mid_point_dist)

        center = LatLon(area.location.lat, area.location.lng)

        coords = [center] + \
            select_coords_in_heading(d, center, north) + \
            select_coords_in_heading(d, center, south) + \
            select_coords_in_heading(d, center, east) + \
            select_coords_in_heading(d, center, west) + \
            select_coords_in_heading(d, center, ne) + \
            select_coords_in_heading(d, center, nw) + \
            select_coords_in_heading(d, center, se) + \
            select_coords_in_heading(d, center, sw)

        return coords



    lat_lngs = generate_lat_lngs(d, area)

    addresses = [get_address_from_lat_lng(l) for l in lat_lngs]
    return [create_location_result(a) for a in addresses if a is not None]

"""
This generates a dataset of house addresses inside an area
"""
@click.command()
@click.option('--name', help='Area name', required=True)
@click.option('--d', help='Mile increments in which to get addresses', default=1)
@click.option('--out', default='/dev/stdout', help='Write out to path')
def gen_addrs(name, d, out):
    results = get_location_data(name)
    area = results[0]

    # get addresses in increments
    res = get_addresses(d, area)
    with open(out, 'w') as f:
        f.write(json.dumps([json.loads(r.model_dump_json()) for r in res]))

@click.command(help='Retrieves historical house data for addresses in input file. Addresses must follow Location schema')
@click.option('--i', help='File to read Locations data from', type=click.Path(exists=True))
def house_info(i: str):
    addresses = []
    with open(i, 'r') as f:
        addresses = [Location(**l) for l in json.load(f)]

    grouped_addreses = itertools.groupby(
            sorted(addresses, key=lambda x: f"{x.county.name} {x.county.state}"), lambda x: x.county)
    for (county, addreses) in grouped_addreses:
        print(county)
        print(addresses)

@click.group()
def cli():
    pass

cli.add_command(gen_addrs)
cli.add_command(house_info)

if __name__ == '__main__':
    cli()
