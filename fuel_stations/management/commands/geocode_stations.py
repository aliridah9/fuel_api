# fuel_stations/management/commands/geocode_stations.py
from geopy.geocoders import Nominatim
from fuel_stations.models import FuelStation
import time

def geocode_stations():
    geolocator = Nominatim(user_agent="fuel_api")
    for station in FuelStation.objects.all():
        try:
            location = geolocator.geocode(f"{station.address}, {station.city}, {station.state}")
            if location:
                station.location = {
                    "type": "Point",
                    "coordinates": [location.longitude, location.latitude]
                }
                station.save()
                time.sleep(1)  # Rate limit
        except Exception as e:
            print(f"Error geocoding {station.name}: {e}")