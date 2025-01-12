import csv
import requests
from django.core.management.base import BaseCommand
from django.conf import settings

CHUNK_SIZE = 1000

class Command(BaseCommand):
    help = """Geocode addresses from a CSV file using Geoapify Batch Geocoding API."""

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file.')

    def handle(self, *args, **options):
        file_path = options['file_path']

        addresses = []        
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                full_address = f"{row['Address']}, {row['City']}, {row['State']}"
                addresses.append(full_address)


        batch_url = f"https://api.geoapify.com/v1/batch/geocode/search?apiKey={settings.GEOAPIFY_API_KEY}"
        headers = {"Content-Type": "application/json"}
        address_chunks = [addresses[i:i + CHUNK_SIZE] for i in range(0, len(addresses), CHUNK_SIZE)]
        for chunk_of_addresses in address_chunks:
            response = requests.post(batch_url, json=chunk_of_addresses, headers=headers)
            response.raise_for_status()
            results = response.json()
