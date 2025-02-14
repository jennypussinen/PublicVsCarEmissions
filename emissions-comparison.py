import requests
import json
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

with open("config.json", "r") as f:
    config = json.load(f)

OPENROUTE_API_KEY = config["OPENROUTE_API_KEY"]
DIGITRANSIT_API_KEY = config["DIGITRANSIT_API_KEY"]

def format_route_summary(response):
    total_walk_distance = 0
    total_drive_distance = 0
    
    if isinstance(response, str):
        response = json.loads(response)
    
    # Extract the steps from the response
    steps = response['features'][0]['properties']['segments'][0]['steps']
    
    # Loop through each step and accumulate the walking and driving distances
    for step in steps:
        if step['type'] == 11:  
            total_walk_distance += step['distance']
        elif step['type'] in [0, 1, 5, 13]: 
            total_drive_distance += step['distance']
    
    # Convert distances from meters to kilometers
    total_walk_distance_km = total_walk_distance / 1000
    total_drive_distance_km = total_drive_distance / 1000
    
    # Print the format for walk -> drive
    print(f"Walk {total_walk_distance_km} km -> Drive {total_drive_distance_km} km")
    
    # Return the drive distance
    return total_drive_distance_km

def get_route(origin_lat, origin_lon, dest_lat, dest_lon):
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    }

    url = f'https://api.openrouteservice.org/v2/directions/driving-car?api_key={OPENROUTE_API_KEY}&start={origin_lon},{origin_lat}&end={dest_lon},{dest_lat}'
    
    call = requests.get(url, headers=headers)
    
    # Print the response text (raw JSON)
    return format_route_summary(call.text)

def get_public_transportation_options(origin_lat, origin_lon, dest_lat, dest_lon):
    query = gql(f'''
    {{
      planConnection(
        origin: {{location: {{coordinate: {{latitude: {origin_lat}, longitude: {origin_lon}}}}}}}
        destination: {{location: {{coordinate: {{latitude: {dest_lat}, longitude: {dest_lon}}}}}}}
        first: 1
      ) {{
        pageInfo {{
          endCursor
        }}
        edges {{
          node {{
            start
            end
            legs {{
              duration
              mode
              distance
              start {{
                scheduledTime
              }}
              end {{
                scheduledTime
              }}
              mode
              duration
              realtimeState
            }}
            emissionsPerPerson {{
              co2
            }}
          }}
        }}
      }}
    }}
    ''')

    transport = RequestsHTTPTransport(
        url="https://api.digitransit.fi/routing/v2/waltti/gtfs/v1",
        headers={
            "Content-Type": "application/json",
            "digitransit-subscription-key": DIGITRANSIT_API_KEY
        }
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    try:
        result = client.execute(query)
        return format_transportation_options(result)
    except Exception as e:
        print(f"Failed to fetch transportation options: {e}")
        return None

def get_lat_lon(street_name: str):
    url = "http://api.digitransit.fi/geocoding/v1/search"
    headers = {
        "Content-Type": "application/json",
        "digitransit-subscription-key": DIGITRANSIT_API_KEY
    }
    params = {
        "text": street_name,
        "size": 1
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        features = data.get("features", [])
        if features:
            location = features[0].get("geometry", {}).get("coordinates", [])
            if len(location) == 2:
                lon, lat = location
                print("Coordinates found")
                return lat, lon  
            else:
                raise ValueError("Coordinates not found")
        else:
            raise ValueError("Address not found")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")

def format_transportation_options(data):
    formatted_route = []
    bus_distance = 0
    tram_distance = 0
    rail_distance = 0
    
    # Extract the legs from the response
    legs = data.get('planConnection', {}).get('edges', [])[0].get('node', {}).get('legs', [])
    
    # Process each leg and accumulate distances for bus and tram
    for leg in legs:
        mode = leg.get('mode', 'Unknown mode')
        distance = leg.get('distance', 0)
        formatted_route.append(f"{mode} {distance:.0f}m")
        
        if mode.lower() == 'bus':
            bus_distance += distance
        elif mode.lower() == 'tram':
            tram_distance += distance
        elif mode.lower() == 'rail':
            rail_distance += distance
    
    # Convert distances from meters to kilometers
    bus_distance_km = (bus_distance / 1000)
    tram_distance_km = (tram_distance / 1000)
    rail_distance_km = (rail_distance / 1000)
    
    # Print the formatted route and return the total distances
    print(" -> ".join(formatted_route))
    return bus_distance_km, tram_distance_km, rail_distance_km

def calculate_emissions(bus_km, tram_km, rail_km, car_km):
    # values based on https://www.navit.com/resources/bus-train-car-or-e-scooter-carbon-emissions-of-transport-modes-ranked
    # CO2 emission values based on g/pkm (grams per person-kilometre)
    car_co2 = 166  # g/pkm for car
    bus_co2 = 93   # g/pkm for bus
    rail_co2 = 58  # g/pkm for rail
    tram_co2 = 63  # g/pkm for tram
    

    car_emissions = car_co2 * car_km
    bus_emissions = bus_co2 * bus_km
    rail_emissions = rail_co2 * rail_km
    tram_emissions = tram_co2 * tram_km


    print(f"Public transportation CO2 emissions: {bus_emissions+tram_emissions+rail_emissions:.2f} g (bus + tram + rail {bus_km + tram_km + rail_km:.2f}km)")
    print(f"Car CO2 emissions: {car_emissions:.2f} g (car {car_km:.2f}km)")

    


try:
    originStreet = input("Enter origin street name: ")
    oLat, oLon = get_lat_lon(originStreet)  
    print(oLat, oLon)

    destinationStreet = input("Enter destination street name: ")
    dLat, dLon = get_lat_lon(destinationStreet)  
    print(dLat, dLon)

    bus_km, tram_km, rail_km = get_public_transportation_options(oLat, oLon, dLat, dLon)
    car_km = get_route(oLat, oLon, dLat, dLon)

    calculate_emissions(bus_km, tram_km, rail_km, car_km)

except Exception as e:
    print(f"An error occurred: {e}")