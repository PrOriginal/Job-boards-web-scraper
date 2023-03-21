import requests
import re
import unicodedata
import csv
import os
import json
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}

def create_path(file_name):
	desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
	complete_name = os.path.join(desktop, file_name)
	return complete_name

def get_date():
	today = datetime.today().strftime('%d.%m.%y')
	return today

def write_json(price_data):
	file_name = create_path("RTV AGD data.json")
	json_object = json.dumps(price_data, indent=4)
	with open(file_name, "w") as file:
		file.write(json_object)

def open_json():
	file_name = create_path("RTV AGD data.json")
	if not os.path.exists(file_name):
		print("file doesn't exists")
		exit()
	with open(file_name) as file:
		price_data = json.load(file)
	return	price_data

def write_xlsx():
	price_data = open_json()
	file_name = create_path("Price Tables.xlsx")
	with pd.ExcelWriter(file_name) as writer:
		for name in price_data.keys():
			
			name.to_excel(writer , sheet_name = name)


def write_data_dict(names, prices):
	today = get_date()
	price_data = open_json()
	for i in range(len(names)):
		if names[i] not in price_data.keys():
			price_data.update({names[i]:{today:prices[i]}})
		else:
			pair = {today:prices[i]}
			price_data[names[i]].update(pair)
	write_json(price_data)
	
def write_csv(price_data):
	csv_header = ["Date", "Laptop", "Price"]
	today = get_date()
	file_name = create_path("RTV AGD prices.csv")

	if not os.path.exists(file_name):
		with open(file_name, "w") as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=csv_header)
			writer.writeheader()
			for key, item in price_data.items():
				csvfile.write("%s, %s, %s\n" % (today, key, item))
	else:
		with open(file_name, "a") as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=csv_header)
			for key, item in price_data.items():
				csvfile.write("%s, %s, %s\n" % (today, key, item))

def print_price_data(names,prices):
	price_data = {names[i]: prices[i] for i in range(len(names))}
	for laptop, price in price_data.items():
		print(f"{laptop}:\n{price} PLN")
		print("-----------------------------------------------------------------")

def rtv_agd(headers):
	URL = 'https://www.euro.com.pl/laptopy-i-netbooki,d3,rodzaj-procesora_3!intel-core-i7:intel-core-i5:intel-core-m-series:5:6,l2,dy278:279:306:308:318:352:354,do3900.bhtml'
	page = requests.get(URL, headers=headers)
	soup = BeautifulSoup(page.content, "html.parser")
	div_products = soup.find('div', id="products")

	names = []
	i = 1
	for name in div_products.find_all("h2", class_="product-name"):
		if i % 2 == 0:
			name = name.get_text().strip()
			name = re.sub(r'\d+,\d".*\s[i]', "- i", name)
			names.append(name)
		i += 1

	prices = []
	for price in soup.find_all("div", class_="product-prices-box"):
		normalized_price = unicodedata.normalize('NFKD', price.get_text())
		normalized_price = re.sub('\s+', "", normalized_price)
		prices.append(int(normalized_price[0:4]))

	#write_csv(price_data)
	#write_xlsx()
	print_price_data(names,prices)
	write_data_dict(names,prices)

def media_expert():
	URL = "https://www.mediaexpert.pl/komputery-i-tablety/laptopy-i-ultrabooki/laptopy/procesor_intel-core-i5.intel-core-i7.intel-core-i9/karta-graficzna_nvidia-geforce-gtx.nvidia-geforce-rtx.nvidia-quadro/wielkosc-pamieci-ram-gb_16/cena_0.3900?sort=price_asc"


while True:
	try:
		rtv_agd(headers)
	except AttributeError:
		print("Error, trying again...")
		continue
	break

URL1 = "https://www.mediaexpert.pl/komputery-i-tablety/laptopy-i-ultrabooki/laptopy/laptop-asus-tuf-gaming-f15-fx506hc-15-6-ips-144hz-i5-11400h-16gb-ram-512gb-ssd-geforce-rtx3050"


def find_price():
	page = requests.get(URL1, headers=headers)
	soup = BeautifulSoup(page.content, "html.parser")

	price = soup.find(class_="whole").get_text()
	match = re.search(r"", price)

	print(type(price))

# page = requests.get(URL2, headers=headers)
# soup = BeautifulSoup(page.content, "html.parser")
# items = []
# for item in soup.find_all(attrs={'class':'name is-section'}):
#   items.append(item.get_text())
#items=[item.get_text() for item in soup.find_all("h2",class_="name is-section")]


#price = soup.find_all("span data-v-48597678")
# print(len(price))
