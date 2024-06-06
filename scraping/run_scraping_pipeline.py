from src.remax.RemaxScraper import RemaxScraper
from src.era.ERAScraper import ERAScraper
from datetime import datetime
import pandas as pd
import time

OUTPUT_DIR = 'gathered_data'
ERA_COOKIE = 'src/era/cookies.json'

now = datetime.now()
date_str = now.strftime("%d_%m_%Y")

start_time = time.time()

# REMAX
concelhos = ['Vila Real']

remax_listings = []

print('Starting Remax scraper...')
for concelho in concelhos:
    scraper = RemaxScraper(num_houses=10000,  # maximum number of houses to scrape
                            city=concelho)
    print(f"Scraping data from {concelho}...")
    listings_concelho = scraper.run(save=False, verbose=False)
    end_time = time.time()
    remax_listings.append(listings_concelho)

remax_listings_df = pd.concat(remax_listings, ignore_index=True)
filename = f"{OUTPUT_DIR}/remax_portugal_{date_str}.csv"
remax_listings_df.to_csv(filename)
print('Remax data has been succesfully scraped!')

# ERA
shape = [
    {"lat": 42.154500, "lng": -9.500000},
    {"lat": 42.154500, "lng": -6.189814},
    {"lat": 36.979792, "lng": -6.189814},
    {"lat": 36.979792, "lng": -9.500000},
    {"lat": 42.154500, "lng": -9.500000}
]

print('Starting ERA scraper...')
# here we have to make sure that there is a cookies.json in path
scraper = ERAScraper(city=None, shape=shape, cookies_file=ERA_COOKIE)
ERA_listings_df = scraper.run(save=False, verbose=False)
filename = f"{OUTPUT_DIR}/era_portugal_{date_str}.csv"
ERA_listings_df.to_csv(filename)
print('ERA data has been succesfully scraped!')

end_time = time.time()
print(f"It took {round((end_time - start_time)/60, 0)} minutes to execute data scraping pipeline.")