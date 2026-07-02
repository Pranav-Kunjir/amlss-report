"""
Step 1: Find the API endpoint by intercepting network requests on the Unstop page.
"""
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

options = Options()
options.binary_location = "/usr/bin/google-chrome-stable"
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

driver = webdriver.Chrome(options=options)

url = "https://unstop.com/hackathons/crp-amazon-ml-summer-school-2026-amazon-1688859/online-assessment/439416"
print(f"Loading: {url}")
driver.get(url)

# Wait for the page to load and make API calls
time.sleep(10)

# Extract network logs
logs = driver.get_log("performance")
api_urls = set()

for entry in logs:
    try:
        log = json.loads(entry["message"])["message"]
        if log["method"] == "Network.requestWillBeSent":
            req_url = log["params"]["request"]["url"]
            if "api" in req_url.lower() and ("assessment" in req_url.lower() or "leaderboard" in req_url.lower() or "participant" in req_url.lower() or "shortlist" in req_url.lower()):
                api_urls.add(req_url)
    except (KeyError, json.JSONDecodeError):
        pass

print(f"\nFound {len(api_urls)} relevant API URLs:")
for u in sorted(api_urls):
    print(f"  {u}")

# Also dump ALL api calls for debugging
print("\n--- ALL API calls ---")
for entry in logs:
    try:
        log = json.loads(entry["message"])["message"]
        if log["method"] == "Network.requestWillBeSent":
            req_url = log["params"]["request"]["url"]
            if "unstop.com/api" in req_url:
                print(f"  {req_url}")
    except (KeyError, json.JSONDecodeError):
        pass

driver.quit()
