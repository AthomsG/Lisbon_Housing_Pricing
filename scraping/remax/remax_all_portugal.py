from RemaxScraper import RemaxScraper
import time

start_time = time.time()
concelhos = ['Aveiro', 
             'Beja', 
             'Braga', 
             'Braganca', 
             'Castelo Branco', 
             'Coimbra', 
             'Evora', 
             'Faro', 
             'Guarda', 
             'Leiria', 
             'Lisboa', 
             'Portalegre', 
             'Porto', 
             'Santarem', 
             'Setubal', 
             'Viana do Castelo', 
             'Vila Real', 
             'Viseu']

for concelho in concelhos:
    scraper = RemaxScraper(num_houses=10000,  # maximum number of houses to scrape
                            city=concelho)
    scraper.run()
    end_time = time.time()

print(f"It took {round((end_time - start_time)/60, 0)} minutes to execute data scraping pipeline.")