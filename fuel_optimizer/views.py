from django.http import JsonResponse
import requests
from .models import FuelStation
from opencage.geocoder import OpenCageGeocode
from rest_framework.views import APIView
from geopy.distance import geodesic
from django.conf import settings


class RouteOptimizationView(APIView):
    def post(self, request):

        start_location = request.data.get("start_location")
        finish_location = request.data.get("finish_location")

        if not start_location or not finish_location:
            return JsonResponse(
                {"error": "Both start and finish locations are required."}, status=400
            )

        start_coords = self.geocode_location(start_location)
        finish_coords = self.geocode_location(finish_location)
        if not start_coords or not finish_coords:
            return JsonResponse(
                {"error": "Could not geocode one or both locations."}, status=400
            )

        route = self.fetch_route_from_api(start_coords, finish_coords)
        if not route:
            return JsonResponse(
                {"error": "Could not fetch route from API."}, status=500
            )
        fuel_data = self.calculate_fuel_cost(route, FuelStation.objects.all())
        total_cost = fuel_data["total_cost"]
        stops = fuel_data["fuel_stops"]
        return JsonResponse(
            {"route": route, "fuel_stops": stops, "total_cost": total_cost}
        )
    def geocode_location(self, address):
            geocoder = OpenCageGeocode(settings.OPENCAGE_API_KEY)
            try:
                results = geocoder.geocode(address)
                if results:
                    location = results[0]['geometry']
                    return location['lat'], location['lng']
            except Exception as e:
                print(f"Error geocoding {address}: {e}")
            return None


    def fetch_route_from_api(self, start_coords, finish_coords):

        api_url = "https://api.openrouteservice.org/v2/directions/driving-car"
        api_key = settings.OPENROUTESERVICE_API_KEY
        params = {
            "api_key": api_key,
            "start": f"{start_coords[1]},{start_coords[0]}",
            "end": f"{finish_coords[1]},{finish_coords[0]}",
        }

        try:
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                route_coords = data["features"][0]["geometry"]["coordinates"]
                return [(lat, lon) for lon, lat in route_coords]
        except Exception as e:
            print(f"Error fetching route: {e}")
        return None

    def calculate_fuel_cost(
        self, route, fuel_stations, vehicle_mpg=10, vehicle_range=500
    ):

        total_distance = 0
        total_cost = 0
        fuel_stops = []
        remaining_range = vehicle_range

        for i in range(len(route) - 1):
            segment_distance = geodesic(route[i], route[i + 1]).miles
            total_distance += segment_distance

            if remaining_range < segment_distance:
                nearest_station = self.find_nearest_fuel_station(
                    route[i], fuel_stations
                )
                if nearest_station:
                    fuel_needed = (
                        vehicle_range - remaining_range
                    ) / vehicle_mpg  # gallons
                    total_cost += fuel_needed * nearest_station["retail_price"]
                    fuel_stops.append(
                        {
                            "station_name": nearest_station["name"],
                            "address": nearest_station["address"],
                            "city": nearest_station["city"],
                            "state": nearest_station["state"],
                            "price": nearest_station["retail_price"],
                            "location": (
                                nearest_station["latitude"],
                                nearest_station["longitude"],
                            ),
                        }
                    )
                    remaining_range = vehicle_range
                else:
                    raise ValueError(
                        f"No fuel station found within range near {route[i]}. Stopping."
                    )

            remaining_range -= segment_distance

        return {"total_cost": total_cost, "fuel_stops": fuel_stops}

    def find_nearest_fuel_station(self, current_location, fuel_stations):

        nearest_station = None
        min_distance = float("inf")

        for station in fuel_stations:
            station_coords = (station.latitude, station.longitude)
            distance = geodesic(current_location, station_coords).miles

            if distance < min_distance:
                min_distance = distance
                nearest_station = {
                    "name": station.name,
                    "address": station.address,
                    "city": station.city,
                    "state": station.state,
                    "retail_price": station.retail_price,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                }

        return nearest_station
