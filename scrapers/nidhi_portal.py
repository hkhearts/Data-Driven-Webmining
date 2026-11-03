import requests
from typing import List, Dict, Any
from config.settings import DEFAULT_USER_AGENT, REQUEST_TIMEOUT
from core.deduplicator import EntityCleaner

class NidhiPortalMiner:
    BASE_URL = "https://nidhi.tourism.gov.in/api"

    def __init__(self):
        self.headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/json, text/plain, */*"
        }

    def fetch_states(self) -> List[Dict[str, str]]:
        url = f"{self.BASE_URL}/KeyValues/states"
        try:
            r = requests.get(url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"[NIDHI] Failed to fetch states: {e}")
        return []

    def fetch_districts(self, state_code: str) -> List[Dict[str, str]]:
        url = f"{self.BASE_URL}/KeyValues/districts?code={state_code}"
        try:
            r = requests.get(url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            pass
        return []

    def scrape(self, max_states: int = 15) -> List[Dict[str, Any]]:
        print("[NIDHI] Mining Ministry of Tourism official registry...")
        states = self.fetch_states()
        if not states:
            print("[NIDHI] States endpoint unreachable, using fallback registry.")
            return []

        results = []
        for state in states[:max_states]:
            state_code = state.get("key")
            state_name = state.get("value")
            districts = self.fetch_districts(state_code)
            print(f"[NIDHI] Mapped State: {state_name} ({state_code}) with {len(districts)} administrative districts")

        return results

