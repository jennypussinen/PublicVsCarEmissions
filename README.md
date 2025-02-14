# Transportation Emissions Comparison

This project is part of the *Sustainable Software Engineering* course (COMP.SE.221) at Tampere University. The objective is to integrate data from two different APIs. I chose to compare the CO2 emissions of public transportation (bus, tram, rail) against car travel between two given street addresses.

The project uses the [OpenRouteService](https://openrouteservice.org/) API to fetch driving routes and the [Digitransit](https://digitransit.fi/) API to obtain public transportation options. The emissions for both transportation modes are calculated and compared.

## Features
- Get geographical coordinates (latitude and longitude) for any given street address.
- Fetch driving routes and distances using the OpenRouteService API.
- Fetch public transportation options (bus, tram, rail) and distances using the Digitransit API.
- Calculate and compare CO2 emissions based on the distance traveled using different transportation modes.
- Present a formatted summary of routes and their respective emissions.

## Requirements
- Python 3.7 or higher
- Required libraries:
  - `requests`
  - `gql`

## Installation
1. Clone the repository to your local machine:
    ```bash
    git clone <repository-url>
    ```

2. Install the necessary dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `config.json` file in the root directory with the following structure:
    ```json
    {
        "OPENROUTE_API_KEY": "your-openroute-api-key",
        "DIGITRANSIT_API_KEY": "your-digitransit-api-key"
    }
    ```

4. Replace `"your-openroute-api-key"` and `"your-digitransit-api-key"` with your API keys. You can obtain these keys by registering for the respective APIs:
    - [OpenRouteService](https://openrouteservice.org/sign-up/)
    - [Digitransit](https://digitransit.fi/en/developers/)

## Usage
1. Run the Python script:
    ```bash
    python transport_emissions.py
    ```

2. Enter the origin and destination street names when prompted. The script will calculate and display the CO2 emissions for both public transportation and car travel.

> The API supports addresses within the Tampere region.

Example input:

    Example input:
    ```
    Enter origin street name: kalevantie 4
    Enter destination street name: korkeakoulunkatu 1
    ```

3. The output will include:
    - Public transportation route (bus, tram, rail)
    - Total public transportation distance
    - CO2 emissions for public transportation and car

## Example Output

```bash
Enter origin street name: kalevantie 4
Origin coordinates: 61.494361, 23.780307

Enter destination street name: korkeakoulunkatu 1
Destination coordinates: 61.449775, 23.856846

--- Public transportation route ---
WALK 0.11km -> BUS 2.13km -> WALK 0.10km -> TRAM 5.25km -> WALK 0.51km
--- Car route ---
WALK 0.05 km -> DRIVE 7.47 km


Public transportation CO2 emissions: 528.87 g (bus + tram + rail 7.38 km)
Car CO2 emissions: 1239.89 g (car 7.47 km)
```

## Acknowledgements
- [OpenRouteService](https://openrouteservice.org/)
- [Digitransit](https://digitransit.fi/)
- [NAVIT](https://www.navit.com/resources/bus-train-car-or-e-scooter-carbon-emissions-of-transport-modes-ranked): Source for co2 emissions

