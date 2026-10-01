import requests
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from .models import RiverReading

RIVERWATCH_API_URL = 'https://api.riverwatch.lk/v1/stations/summary'

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

def fetch_riverwatch_data():
    print("Connecting to RiverWatch API...")

    try:
        response = requests.get(
            RIVERWATCH_API_URL,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        print(f'RiverWatch API connected: '
              f'HTTP {response.status_code}'
            )
        
    except requests.RequestException as error:
        print(f'RiverWatch API error: {error}')
        return []

    try:
        data = response.json()

    except ValueError:
        print('ERROR: RiverWatch did not return JSON.')
        return []

    if not isinstance(data, list):
        print('ERROR: Unexpected API response format.')
        return []

    print(f'Recieved {len(data)} station readings.')

    return data


def scrape_riverwatch():
    data = fetch_riverwatch_data()
    readings = []

    for item in data:
        alert_levels = item.get('alertLevels', {})

        last_updated = item.get('lastUpdated')
        parsed_last_updated = None
        if last_updated:
            parsed_last_updated = parse_datetime(last_updated)
            if (parsed_last_updated and timezone.is_naive(parsed_last_updated) ):
                parsed_last_updated = timezone.make_aware(parsed_last_updated)

        reading = {
            'station_name': item.get('name', 'Unknown Station'),
            'river_name': item.get('riverName', 'Unknown River'),
            'water_level': item.get('currentLevel'),
            'previous_level': item.get('previousLevel'),
            'unit': item.get('unit', 'ft'),
            'status': item.get('status', 'Unknown'),
            'minor_level': alert_levels.get('minor'),
            'alert_level': alert_levels.get('alert'),
            'major_level': alert_levels.get('major'),
            'station_id': item.get('id'),
            'river_id': item.get('riverId', ''),
            'last_updated': parsed_last_updated, 
            'station_url': (
                f'https://riverwatch.lk/station/{item.get('id')}' 
                if item.get("id") 
                else None
            ),
        }

        if reading['station_id']: readings.append(reading)

    print(f'Successfully processed {len(readings)} readings.')

    return readings


def save_riverwatch_readings():
    readings = scrape_riverwatch()

    if not readings:
        print('No RiverWatch readings recieved.')
        return []

    saved = []

    created_count = 0
    updated_count = 0

    for item in readings:
        station_id = item['station_id']
        reading, created = (RiverReading.objects.update_or_create(
            station_id=station_id,
            defaults={
                'station_name': item['station_name'],
                'river_name': item['river_name'],
                'water_level': item['water_level'],
                'previous_level': item['previous_level'],
                'unit': item['unit'],
                'status': item['status'],
                'minor_level': item['minor_level'],
                'alert_level': item['alert_level'],
                'major_level': item['major_level'],
                'river_id': item['river_id'],
                'last_updated': item['last_updated'],
                'station_url': item['station_url'],
            }
        ))

        if created:
            created_count += 1
        else:
            updated_count += 1

        saved.append(reading)

    print(f'Created: {created_count}')
    print(f'Updated: {updated_count}')

    return saved