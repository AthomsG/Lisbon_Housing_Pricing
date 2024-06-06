import requests
import json
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

with open('cookies.json', 'r') as f:
    data = json.load(f)
    cookies = data['cookies']
    requestverificationtoken = data['requestverificationtoken']

url = "https://www.era.pt/API/ServicesModule/Property/Search"

payload = {
    "businessTypeId": [1],
    "propertiesTypeId": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "locationId": [],
    "shape": [
        {"lat": 42.154500, "lng": -9.500000},
        {"lat": 42.154500, "lng": -6.189814},
        {"lat": 36.979792, "lng": -6.189814},
        {"lat": 36.979792, "lng": -9.500000},
        {"lat": 42.154500, "lng": -9.500000}
    ],
    "validatePropertyReference": None,
    "sellPrice": None,
    "rentPrice": None,
    "subleasePrice": None,
    "netArea": None,
    "landArea": None,
    "rooms": None,
    "wcs": None,
    "parking": None,
    "onlyDevelopments": False,
    "page": 1
}

headers = {
    "cookie": "; ".join([f"{key}={value}" for key, value in cookies.items()]),
    "origin": "https://www.era.pt",
    "referer": "https://www.era.pt/comprar?ob=1&tp=1,2&sp=a|ykF|oby@gdEecJ_zK}{uAf|_@a~P`hYp|dBaeg@raM&page=1&ord=3",
    "requestverificationtoken": requestverificationtoken,
}

def fetch_references_for_page(page, headers, payload):
    payload_copy = payload.copy()
    payload_copy['page'] = page
    response = requests.post(url, json=payload_copy, headers=headers)
    if response.status_code == 200:
        output = response.json()
        return output.get('PropertyList', [])
    return []

def get_property_references(headers, payload):
    references = []
    first_request = requests.post(url, json=payload, headers=headers)
    if first_request.status_code != 200:
        return references
    
    first_output = first_request.json()
    total_pages = first_output.get('TotalPages', 1)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_references_for_page, page, headers, payload) for page in range(1, total_pages + 1)]
        
        for future in tqdm(as_completed(futures), total=total_pages, desc="Fetching property references", unit="page"):
            property_list = future.result()
            if property_list:
                references.extend([property['Reference'] for property in property_list])

    return references

def get_property_details(headers, reference):
    detail_url = f"https://www.era.pt/API/ServicesModule/Property/PropertyDetailByReference?reference={reference}"
    response = requests.get(detail_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

references = get_property_references(headers, payload)

property_data = []

def fetch_property_detail(reference):
    detail = get_property_details(headers, reference)
    if detail:
        return {
            "Reference": reference,
            "Description": detail.get("Description"),
            "Price": detail.get("SellPrice", {}).get("Value"),
            "Rooms": detail.get("Rooms"),
            "Wcs": detail.get("Wcs"),
            "Latitude": detail.get("Lat"),
            "Longitude": detail.get("Lng"),
            "District": detail.get("LocalizationDetail", {}).get("District"),
            "County": detail.get("LocalizationDetail", {}).get("County"),
            "Parish": detail.get("LocalizationDetail", {}).get("Parish"),
            "Zone": detail.get("LocalizationDetail", {}).get("Zone"),
        }
    return None

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_property_detail, reference) for reference in references]
    for future in tqdm(as_completed(futures), total=len(references), desc="Fetching property details", unit="property"):
        result = future.result()
        if result:
            property_data.append(result)

df = pd.DataFrame(property_data)
df.to_csv("property_data.csv", index=False)