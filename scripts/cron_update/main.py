from os import environ

import requests

from dotenv import load_dotenv
load_dotenv()

API_URL = environ.get("API_URL")
API_KEY = environ.get("API_KEY")

# i.e ["better", "mannys", "haworth"]
print("Getting site list...")
sites = requests.get(f"{API_URL}/api/scraper/list", headers={"Authorization": "Bearer " + API_KEY}).json()

for site in sites:
  print(f"Queuing {site}...")
  req = requests.post(f"{API_URL}/api/scraper/{site}", headers={"Authorization": "Bearer " + API_KEY})
  
  if req.ok:
    print("Queued!")
  else:
    print("Error :(", req.content)
