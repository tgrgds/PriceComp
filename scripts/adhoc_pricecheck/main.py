############
# This takes a list of Musipos Products (products.csv)
# and outputs the best price to sale.csv based on some criteria
############

import csv, requests
from os import environ

from dotenv import load_dotenv
load_dotenv()

API_URL = environ.get("API_URL")
API_KEY = environ.get("API_KEY")

with open("products.csv", "r") as csvfile:
  reader = csv.DictReader(csvfile, ["Supplier_Item_ID","Title","Supplier_RRP","Publisher_Brand","Instrument","Quantity_on_hand","Minimum_Sell","COST","SALE PRICE","MARGIN"])

  with open("sale.csv", "w") as writefile:
    writer = csv.writer(writefile)

    writer.writerow(["sku", "rrp", "price", "margin", "competitor", "link"])

    for row in reader:
      stores = requests.get(f"{API_URL}/api/product/search/{row['Supplier_Item_ID']}?strict=1", headers={"Authorization": "Bearer " + API_KEY})

      if not stores.ok: continue

      stores = stores.json()
      print(stores)

      lowest_price = 999999999999
      lowest_store = ""

      for store in stores:
        price = float(store["price"])
        if price < lowest_price and (price - float(row["COST"]))/price > 0.1:
          lowest_price = price
          lowest_store = store["store_id"]
        
      if lowest_price < 999999999999 and lowest_price > float(row["Minimum_Sell"]):
        writer.writerow([row["Supplier_Item_ID"], row["Supplier_RRP"], lowest_price, (lowest_price - float(row["COST"]))/lowest_price, lowest_store])