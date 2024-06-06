import requests
import json
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class ERAScraper:
    def __init__(self, city, shape, cookies_file='cookies.json'):
        self.city = city
        self.shape = shape
        self.cookies_file = cookies_file
        self.url = "https://www.era.pt/API/ServicesModule/Property/Search"
        self.load_cookies()
        self.payload = {
            "businessTypeId": [1],
            "propertiesTypeId": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            "locationId": [],
            "shape": self.shape,
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
        self.headers = {
            "cookie": "; ".join([f"{key}={value}" for key, value in self.cookies.items()]),
            "origin": "https://www.era.pt",
            "referer": "https://www.era.pt/comprar?ob=1&tp=1,2&sp=a|ykF|oby@gdEecJ_zK}{uAf|_@a~P`hYp|dBaeg@raM&page=1&ord=3",
            "requestverificationtoken": self.requestverificationtoken,
        }
        self.df = None

    def load_cookies(self):
        with open(self.cookies_file, 'r') as f:
            data = json.load(f)
            self.cookies = data['cookies']
            self.requestverificationtoken = data['requestverificationtoken']

    def fetch_references_for_page(self, page):
        payload_copy = self.payload.copy()
        payload_copy['page'] = page
        response = requests.post(self.url, json=payload_copy, headers=self.headers)
        if response.status_code == 200:
            output = response.json()
            return output.get('PropertyList', [])
        return []

    def get_property_references(self):
        references = []
        first_request = requests.post(self.url, json=self.payload, headers=self.headers)
        if first_request.status_code != 200:
            return references

        first_output = first_request.json()
        total_pages = first_output.get('TotalPages', 1)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.fetch_references_for_page, page) for page in range(1, total_pages + 1)]

            for future in tqdm(as_completed(futures), total=total_pages, desc="Fetching property references", unit="page"):
                property_list = future.result()
                if property_list:
                    references.extend([property['Reference'] for property in property_list])

        return references

    def get_property_details(self, reference):
        detail_url = f"https://www.era.pt/API/ServicesModule/Property/PropertyDetailByReference?reference={reference}"
        response = requests.get(detail_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def fetch_property_detail(self, reference):
        detail = self.get_property_details(reference)
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

    def fetch_property_details(self, references):
        property_data = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.fetch_property_detail, reference) for reference in references]
            for future in tqdm(as_completed(futures), total=len(references), desc="Fetching property details", unit="property"):
                result = future.result()
                if result:
                    property_data.append(result)
        return property_data

    def save_to_csv(self):
        now = datetime.now()
        date_str = now.strftime("%d_%m_%Y")
        filename = f"era_{self.city}_{date_str}_properties.csv"
        self.df.to_csv(filename, index=False)
        print(f"Updated data saved to '{filename}'")

    def run(self, save=True):
        references = self.get_property_references()
        property_data = self.fetch_property_details(references)
        self.df = pd.DataFrame(property_data)
        if save:
            self.save_to_csv()
        return self.df.copy()