from django.http import JsonResponse
from django.views.decorators.http import require_GET
import requests
from fuel_stations.models import FuelStation
from geopy.distance import distance

@require_GET
def find_route(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    # Get route from OpenRouteService
    route = get_route(start, end)
    if not route:
        return JsonResponse({'error': 'Routing failed'}, status=400)
    
    # Find stations near the route
    stations = find_nearby_stations(route['geometry'])
    
    # Compute optimal stops
    stops = compute_optimal_stops(route['distance'], stations)
    
    # Calculate total cost
    total_cost = sum(stop['cost'] for stop in stops)
    
    return JsonResponse({
        'stops': stops,
        'total_cost': round(total_cost, 2),
        'route_geometry': route['geometry']
    })

def get_route(start, end):
    api_key = "5b3ce3597851110001cf624867d8c38b92f540ef887bc1d75edcb090"
    url = f"https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {'Authorization': api_key}
    params = {'start': start, 'end': end}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            'distance': data['features'][0]['properties']['segments'][0]['distance'] / 1609.34,  # Convert meters to miles
            'geometry': data['features'][0]['geometry']['coordinates']
        }
    return None

def find_nearby_stations(route_geometry, max_distance=10):
    # Convert max_distance to meters (MongoDB uses meters for distance)
    max_distance_meters = max_distance * 1609.34
    
    # Create a LineString for the route
    route_line = {
        "type": "LineString",
        "coordinates": route_geometry
    }
    
    # Find stations near the route using MongoDB's $near operator
    nearby_stations = FuelStation.objects.filter(
        location__near={
            "$geometry": route_line,
            "$maxDistance": max_distance_meters
        }
    )
    
    return list(nearby_stations)

def compute_optimal_stops(total_distance, stations):
    stops = []
    current_range = 500  # Max range in miles
    current_position = 0
    
    while current_position < total_distance:
        next_stop = None
        for station in stations:
            station_pos = station.distance_from_start  # Assume precomputed
            if current_position < station_pos <= current_position + current_range:
                if not next_stop or station.price < next_stop.price:
                    next_stop = station
        
        if not next_stop:
            break  # No station found
        
        distance_covered = next_stop.distance_from_start - current_position
        gallons_needed = distance_covered / 10
        stops.append({
            'name': next_stop.name,
            'cost': gallons_needed * next_stop.price,
            'location': [next_stop.latitude, next_stop.longitude]
        })
        current_position = next_stop.distance_from_start
    
    return stops