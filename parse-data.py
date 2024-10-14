import requests
import json
import csv
from pathlib import Path

date = '2024-10-12'

def scrape_data(location_id, location_period_id, location_name, location_period_name):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://dineoncampus.com',
        'priority': 'u=1, i',
        'referer': 'https://dineoncampus.com/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    params = {
        'platform': '0',
        'date': date,
    }

    response = requests.get(
        f'https://api.dineoncampus.com/v1/location/{location_id}/periods/{location_period_id}',
        params=params,
        headers=headers,
    )

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
        data = {}

    output_dir = Path('data')
    output_dir.mkdir(exist_ok=True)

    menu = data.get('menu', {})
    periods = menu.get('periods', {})
    categories = periods.get('categories', [])
    items = []
    for category in categories:
        category_id = category.get('id', '')
        category_items = category.get('items', [])
        for item in category_items:
            item_data = {
                'dining_hall_name': location_name,
                'meal_type': location_period_name,
                'id': item.get('id', ''),
                'category_name': category.get('name', ''),
                'category_id': category_id,
                'name': item.get('name', ''),
                'mrn': item.get('mrn', ''),
                'mrn_full': item.get('mrn_full', ''),
                'desc': item.get('desc', '') if item.get('desc') is not None else '',
                'webtrition_id': item.get('webtrition_id', ''),
                'sort_order': item.get('sort_order', 0),
                'portion': item.get('portion', ''),
                'qty': item.get('qty', ''),
                'ingredients': item.get('ingredients', ''),
                'custom_allergens': item.get('custom_allergens', '') if item.get('custom_allergens') is not None else '',
                'calories': item.get('calories', '')
            }
            items.append(item_data)

    return items

all_items = []

with open('places-data.json', 'r') as f:
    data = json.load(f)

    for location, location_data in data.items():
        location_id = location_data['id']
        for period in location_data['periods']:
            location_period_id = period['id']
            location_period_name = period['name']
            items = scrape_data(location_id, location_period_id, location, location_period_name)
            all_items.extend(items)

# Write all items to a single CSV file
output_dir = Path('data')
output_dir.mkdir(exist_ok=True)

with open(output_dir / 'all_dining_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'dining_hall_name', 'meal_type', 'id', 'category_name', 'category_id', 'name', 'mrn', 'mrn_full', 'desc', 'webtrition_id',
        'sort_order', 'portion', 'qty', 'ingredients', 'custom_allergens', 'calories'
    ])
    writer.writeheader()
    for item in all_items:
        writer.writerow(item)

print("All dining data has been written to 'all_dining_data.csv' in the 'data' directory.")
