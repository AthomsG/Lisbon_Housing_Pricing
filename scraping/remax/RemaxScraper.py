# remax's URL is basically a query, so we can use it directly to fetch data.
# based on this video: https://www.youtube.com/watch?app=desktop&v=DqtlR0y0suo

"""
It seems that there's a first query to an API that get's as a listing ID and some information.
We then have to get the information from another API, by using the listing ID.
"""

import time
import requests
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime

class RemaxScraper:
    def __init__(self, num_houses, city):
        self.num_houses = num_houses
        self.city = city
        self.url = "https://remax.pt/Api/Listing/MultiMatchSearch"
        self.querystring = {"page":"0","searchValue":f"{self.city}","size":f"{self.num_houses}"}
        self.payload = {
            "filters": [
                {
                    "field": "BusinessTypeID",
                    "value": "1",
                    "type": 0
                },
                {
                    "field": "IsSpecialExclusive",
                    "value": "false",
                    "type": 0
                }
            ],
            "sort": {
                "fieldToSort": "PublishDate",
                "order": 1
            }
        }
        self.headers = {
            "origin": "https://remax.pt",
            "referer": f"https://remax.pt/comprar?searchQueryState=%7B%22regionName%22:%22{self.city}%22,%22businessType%22:1,%22page%22:1,%22regionID%22:%22%22,%22regionType%22:%22%22,%22sort%22:%7B%22fieldToSort%22:%22PublishDate%22,%22order%22:1%7D,%22mapIsOpen%22:false%7D",
        }
        self.df = None

    def fetch_general_data(self):
        response = requests.request("POST", self.url, json=self.payload, headers=self.headers, params=self.querystring)
        data = json.loads(response.text)
        results = data['results']
        keys = ['listingTitle', 'coordinates', 'listingPrice', 'listingTypeID', 'regionName1', 'regionName2', 'regionName3']
        data_extracted = [{key: entry[key] for key in keys} for entry in results]
        self.df = pd.DataFrame(data_extracted)
        self.df['latitude'] = self.df['coordinates'].apply(lambda x: x['latitude'] if x is not None else None)
        self.df['longitude'] = self.df['coordinates'].apply(lambda x: x['longitude'] if x is not None else None)
        self.df = self.df.drop(columns=['coordinates'])

    def fetch_listing_type(self):
        listing_titles = self.df['listingTitle'].unique()
        pbar = tqdm(total=len(listing_titles))

        def fetch_info(listing_title, payload=""):
            url = f"https://s.maxwork.pt/site/static/9/listings/searchdetails_V2/{listing_title}.html"
            response = requests.request("GET", url, data=payload, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            listing_type_elem = soup.find('li', class_='listing-type')
            listing_type = listing_type_elem.text if listing_type_elem else None
            pbar.update()
            return {
                'listing_title': listing_title,
                'listing_type': listing_type,
            }

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(fetch_info, listing_titles))

        pbar.close()
        df_new = pd.DataFrame(results)
        self.df = pd.merge(self.df, df_new, how='left', left_on='listingTitle', right_on='listing_title')

    def fetch_detailed_info(self):
        listing_titles = self.df['listingTitle'].unique()
        pbar = tqdm(total=len(listing_titles))
        key_whitelist = {'Área Bruta Privativa m2', 'Área Bruta m2', 'Área Total do Lote m2', 'Área Útil m2', 'Quartos',
                         'Ano de construção', 'Piso', 'WCs', 'Elevador', 'Estacionamento'}

        def fetch_info(listing_title):
            try:
                url = f"https://s.maxwork.pt/site/static/9/listings/details-mobile_V2/{listing_title}.html"
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                description = soup.find('div', class_='listing-description').text.strip() if soup.find('div', class_='listing-description') else "No description"
                details = {}
                for tr in soup.find_all('tr'):
                    columns = tr.find_all('td')
                    if len(columns) % 2 == 0:
                        for i in range(0, len(columns), 2):
                            key = columns[i].text.strip()
                            value = columns[i + 1].text.strip()
                            if key in key_whitelist:
                                details[key] = value
                energy_efficiency_div = soup.find('div', class_='energy-details')
                energy_efficiency = energy_efficiency_div.find('img', alt=True)['alt'] if energy_efficiency_div and energy_efficiency_div.find('img', alt=True) else 'Not available'
            except requests.exceptions.RequestException as e:
                print(f"Request failed for {listing_title}: {e}")
                return None

            pbar.update()
            return {
                'listingTitle': listing_title,
                'description': description,
                'details': details,
                'energy_efficiency': energy_efficiency
            }

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(filter(None, executor.map(fetch_info, listing_titles)))

        pbar.close()
        df_new = pd.DataFrame(results)
        details_df = df_new['details'].apply(pd.Series)
        df_new = pd.concat([df_new.drop(['details'], axis=1), details_df], axis=1)
        self.df = pd.merge(self.df, df_new, how='left', on='listingTitle')

    def save_to_csv(self):
        now = datetime.now()
        date_str = now.strftime("%d_%m_%Y")
        filename = f"remax_{self.city}_{date_str}_{int(self.num_houses/1e3)}k_general.csv"
        self.df.to_csv(filename, index=False)
        print("Updated data saved to '" + filename + "'")

    def run(self):
        self.fetch_general_data()
        self.fetch_listing_type()
        self.fetch_detailed_info()
        self.save_to_csv()