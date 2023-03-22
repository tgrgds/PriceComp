import os, csv, shutil
from datetime import date
from pathlib import Path

import requests

from email_feed import send_feed_email

from dotenv import load_dotenv
load_dotenv()

cur_path = os.path.dirname(os.path.realpath(__file__))

API_URL = os.environ.get("API_URL")
API_KEY = os.environ.get("API_KEY")

# i.e ["better", "mannys", "haworth"]
sites = requests.get(f"{API_URL}/api/scraper/list", headers={"Authorization": "Bearer " + API_KEY}).json()

# create csv output folder if it doesn't exist
Path(cur_path + "/csv").mkdir(exist_ok=True)

# create the 'old' folder if it doesn't exist
Path(cur_path + "/csv/old").mkdir(exist_ok=True)

# move any already-existing csv files to the /csv/old folder
for file in os.listdir(cur_path + "/csv"):
  filepath = cur_path + "/csv/" + file

  if os.path.isfile(filepath):
    shutil.move(filepath, cur_path + "/csv/old/" + file)

for site in sites:
  print(site)

  products = requests.get(f"{API_URL}/api/product/{site}/all", headers={"Authorization": "Bearer " + API_KEY}).json()

  with open(f"{cur_path}/csv/{site}-{date.today()}.csv", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["sku", "price", "url", "in_stock"], quoting=csv.QUOTE_ALL)

    writer.writeheader()

    for product in products:
      # print(product)
      
      writer.writerow({
        "sku": product["sku"],
        "price": product["price"],
        "url": product["url"],
        "in_stock": product["in_stock"]
      })

print("All files output to the csv directory")

print("Sending email...")
send_feed_email(cur_path + "/csv")
print("Done!")