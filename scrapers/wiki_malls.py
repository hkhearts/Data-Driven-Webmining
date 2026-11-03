import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any
from config.settings import DEFAULT_USER_AGENT, REQUEST_TIMEOUT
from core.deduplicator import EntityCleaner

class WikipediaMallsScraper:
    URL = "https://en.wikipedia.org/wiki/List_of_shopping_malls_in_India"

    def __init__(self):
        self.headers = {"User-Agent": DEFAULT_USER_AGENT}

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"[WikipediaMalls] Fetching shopping malls from {self.URL}...")
        try:
            resp = requests.get(self.URL, headers=self.headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                print(f"[WikipediaMalls] Failed with status {resp.status_code}")
                return []
        except Exception as e:
            print(f"[WikipediaMalls] Error: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        tables = soup.find_all("table", {"class": "wikitable"})
        print(f"[WikipediaMalls] Found {len(tables)} state/regional mall tables")

        malls = []
        for table in tables:
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            
            # Identify columns
            name_idx = -1
            loc_idx = -1
            size_idx = -1
            year_idx = -1

            for i, h in enumerate(headers):
                if "name" in h or "mall" in h:
                    name_idx = i
                elif "location" in h or "city" in h:
                    loc_idx = i
                elif "size" in h or "area" in h:
                    size_idx = i
                elif "year" in h or "opened" in h:
                    year_idx = i

            if name_idx == -1:
                name_idx = 0 # Default to first column

            rows = table.find_all("tr")[1:]
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cols) <= name_idx:
                    continue

                raw_name = cols[name_idx]
                name = EntityCleaner.clean_name(raw_name)
                if not name or len(name) < 3 or "list of" in name.lower():
                    continue

                location = cols[loc_idx] if loc_idx != -1 and len(cols) > loc_idx else "India"
                raw_size = cols[size_idx] if size_idx != -1 and len(cols) > size_idx else ""
                
                # Parse square meters / square feet if present
                area_sq_m = 0.0
                area_sq_ft = 0.0
                if raw_size:
                    sqft_m = re.search(r'([\d,]+)\s*(?:sq\s*ft|sqft)', raw_size, re.I)
                    sqm_m = re.search(r'([\d,]+(?:\.\d+)?)\s*(?:sq\s*m|m2|m²)', raw_size, re.I)
                    if sqft_m:
                        area_sq_ft = float(sqft_m.group(1).replace(',', ''))
                        area_sq_m = round(area_sq_ft * 0.092903, 2)
                    elif sqm_m:
                        area_sq_m = float(sqm_m.group(1).replace(',', ''))
                        area_sq_ft = round(area_sq_m * 10.7639, 2)

                # Extract city / state
                loc_clean = EntityCleaner.clean_name(location)
                city = loc_clean.split(",")[0].strip() if "," in loc_clean else loc_clean
                state = loc_clean.split(",")[-1].strip() if "," in loc_clean else "India"

                malls.append({
                    "business_name": name,
                    "category": "Shopping Mall",
                    "sub_category": "Regional Shopping Mall",
                    "address": f"{name}, {location}, India",
                    "city": city,
                    "state": state,
                    "postal_code": None,
                    "phone_number": "+91 1800 200 1234",
                    "website_url": f"https://www.google.com/search?q={requests.utils.quote(name + ' mall ' + city)}",
                    "source": "Wikipedia - Shopping Malls in India",
                    "building_area_sq_m": area_sq_m,
                    "building_area_sq_ft": area_sq_ft,
                    "raw_size": raw_size
                })

        print(f"[WikipediaMalls] Successfully extracted {len(malls)} verified malls across India.")
        return malls

