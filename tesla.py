import json
import pprint
import time
import threading
import re
import csv
import pandas as pd

from datetime import datetime

from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

def Mbox(title, text, style):
    return 

import ctypes  # An included library with Python install.

html = None
cars = []
zipcsv = pd.read_csv('zipcodes.csv')

zips = zipcsv['zipcode'].tolist()

results_container_selector = 'div.results-container.results-container--grid.results-container--has-results'
delay = 10  # seconds

priceThreshold = 70000
chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

def runner(zipcod):
    try:

        print(datetime.now().strftime("%H:%M:%S") + " Searching Tesla's website")
        url = 'https://www.tesla.com/inventory/new/my?TRIM=PAWD&AUTOPILOT=AUTOPILOT&CABIN_CONFIG=FIVE&ADL_OPTS=PERFORMANCE_UPGRADE&arrangeby=mlh&zip={}&range=200'.format(zipcod)
        browser.get(url)
        # wait for results to be displayed
        WebDriverWait(browser, delay).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, results_container_selector)))
        html = browser.page_source
    except TimeoutException:
        print('Loading took too much time!')
        html = ''
    if len(html) > 0:
        soup = BeautifulSoup(html, 'lxml')
        for car_html in soup.select_one(results_container_selector).findChildren('article'):
            car = {}
            car['price'] = [int(re.sub('[^0-9]', '', car_html.select_one('section.result-header').select_one('div.result-pricing').select_one('span.result-purchase-price').text.replace('€', '').replace(',', '')))]
            car['colour'] = [car_html.select('section.result-features.features-grid')[0].select('ul')[1].select('li')[0].text]
            car['type'] = [car_html.select_one('section.result-header').select_one('div.result-basic-info').select_one('h3').text]
            car['trim'] = [car_html.select_one('section.result-header').select_one('div.result-basic-info').select('div')[0].text]
            car['mileage'] = car_html.select_one('section.result-header').select_one('div.result-basic-info').select('div')[1].text
            car['wheels'] = [re.sub('[^0-9]', '', car_html.select('section.result-features.features-grid')[0].select('ul')[1].select('li')[1].text) + " inch wheels"]
            car['interior'] = [car_html.select('section.result-features.features-grid')[0].select('ul')[1].select('li')[2].text]
            car['link'] = 'https://www.tesla.com/inventory/new/my?TRIM=PAWD&AUTOPILOT=AUTOPILOT&CABIN_CONFIG=FIVE&ADL_OPTS=PERFORMANCE_UPGRADE&arrangeby=mlh&zip={}&range=200'.format(zipcod)
            if(car['price'][0] < priceThreshold and ('Less than 50' in car['mileage'])):
                cars.append(car)   
                df = pd.DataFrame.from_dict(car) 
                # saving the dataframe 
                df.to_csv('Results/' + str(car['price'][0]) + " " + str(cars.index(car)) + " " + zipcod +'.csv') 
                print("FOUND A CAR for $" + str(car['price'][0]))
threads = []
for zipcode in zips:
    if len(threading.enumerate()) < 100:
        t = threading.Thread(target = runner, args = [zipcode])
        threads.append(t)
        t.start()
    else:
        for thread in threads:
            thread.join()
        threads.clear()
        t = threading.Thread(target = runner, args = [zipcode])
        threads.append(t)
        t.start()
browser.quit()