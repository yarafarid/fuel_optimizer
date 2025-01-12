import csv
from django.core.management.base import BaseCommand
from collections import defaultdict
import json

from fuel_optimizer.models import FuelStation


class Command(BaseCommand):
    help = """Geocode addresses from a CSV file using Geoapify Batch Geocoding API."""

    def add_arguments(self, parser):
        parser.add_argument('stations_file', type=str, help='Path to the stations addresses csv file.')
        parser.add_argument('geocoded_stations_file', type=str, help='Path to the gencoded station addresses json file.')

    def handle(self, *args, **options):
        if FuelStation.objects.exists():
            print("Fuel stations already exist in the database.")
            return        

        stations_file = options['stations_file']
        addresses = defaultdict()
        with open(stations_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                full_address = f"{row['Address']}, {row['City']}, {row['State']}"
                """
                Another station in the same location?
                """
                if full_address in addresses:
                    """
                    Exclude it from seed if it's more expensive than the one already in the list.
                    """
                    considered_station_price = float(addresses[full_address]['retail_price'])
                    current_station_price = float(row['Retail Price'])
                    if (considered_station_price <= current_station_price): 
                        continue
                addresses[full_address] = {
                   'opis_id': row['OPIS Truckstop ID'],
                   'name': row['Truckstop Name'],
                   'address': row['Address'],
                   'city': row['City'],
                   'state': row['State'],
                   'retail_price': float(row['Retail Price']),
                   'rack_id': row.get('Rack ID', None),
                   'latitude': None,
                   'longitude': None,
                }

        geocoded_stations_file = options['geocoded_stations_file']
        with open(geocoded_stations_file, 'r') as json_file:
            geocoded_stations = json.load(json_file)

        for station in geocoded_stations:
            full_address = station['query']['text']
            if 'lat' in station and 'lon' in station:
                addresses[full_address].update({
                    'latitude': station['lat'],
                    'longitude': station['lon'],
                })
        
        for station in addresses.values():
            FuelStation.objects.update_or_create(**station)