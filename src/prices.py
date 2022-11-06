import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from lxml import etree as et
import argparse
from tinydb import TinyDB, Query
import datetime

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
}

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--add', default='', type=str)
	parser.add_argument('--update', action='store_true')
	parser.add_argument('--print', action='store_true')
	parser.add_argument('--delete', action='store_true')
	return parser.parse_args()

def get_amazon_product(content):
	'''
	Get product price from html content body.
	'''
	try:
		p = content.xpath('//span[@class="a-offscreen"]/text()')[0]
		p = float(p.replace(',', '').replace('$', '').replace('.00', ''))
	except Exception:
		p = pd.NA
	
	try:
		n = content.xpath('//span[@id="productTitle"]/text()')
		n = n[0].strip()
	except Exception:
		n = "N\A"
	return n, p

def get_from_url(url):
	'''
	Get html content body from Amazon url, runs it through get_amazon_product()
	to get the current price, and then returns price.
	'''
	response = requests.get(url, headers=header)
	soup = bs(response.content, 'html.parser')
	content = et.HTML(str(soup))
	name, price = get_amazon_product(content)
	return name, price


def send_email(item, email):
	'''
	TODO:
		- Send an email to some address saying 'item' is discounted.
	'''
	raise NotImplementedError

def get_historic_prices(item_name, db):
	'''
	TODO:
		Given an item_name, this function finds all entries in the
		db for this item_name, and then sorts their prices in chronological
		order (via 'created_at' column)	and returns a list of the prices.
	'''
	raise NotImplementedError

if __name__ == "__main__":
	args = get_args()
	db = TinyDB("../db/db.json")

	if len(args.add) > 0:
		'''
		Adds a new product to track into our database assuming the url is valid.
		'''
		url = args.add
		name, price = get_from_url(url)
		if name != "N\A":
			db.insert({"name": name, "price": price, "url": url, "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

	if args.update: 
		'''
		We get all products we are tracking, find their current prices, and add a new row into our database with the price + datetime.
		TODO:
			1. After we update the entries, we get all the numbers for each item in the database, and analyze their price.
		'''
		items = set([r["url"] for r in db]) # take set to ensure no duplicates
		c = 0
		for item in items:
			name, price = get_from_url(item)
			if name != "N\A":
				db.insert({"name": name, "price": price, "url": item, "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
				c += 1
		print(f"Updated {c}/{len(items)} items!")
		
		# TODO:
		# 	after this comment line, we want to gather all prices for each item in the database sorted in chronological order
		# 	and then analyze their prices. If some threshold of discount is met, we run the send_email() function on that item.
		# HINT: Implement the get_historic_prices() helper function which returns a list of prices over time sorted chronologically.


	if args.print:
		'''
		Prints the names of all the products we are tracking..
		'''
		items = set([r["name"] for r in db]) 
		print(f"Currently, we are tracking {len(items)} items:")
		for idx, item in enumerate(items):
			print(f"  {idx+1}. {item}")

	if args.delete:
		'''
		TODO:
			1. Print out the items like we do above.
			2. Then, ask the user for input on which item # they want to delete.
			3. Delete all entries from our database db.
		'''
		raise NotImplementedError # delete this line once we implement this.


	# TODO:
	# 	After everything above is implemented, we want to create another python file that automatically calls
	# 	`python3 prices.py --update` periodically.
	# OR (and probably better approach) is set up a cron job on a local machine to automatically call the update.
