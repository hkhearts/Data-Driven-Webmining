import requests
from typing import Optional, Dict, Any, Tuple
from config.settings import GOOGLE_MAPS_API_KEY, DEFAULT_USER_AGENT, REQUEST_TIMEOUT

class DualEngineGeocoder:
    GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    PHOTON_URL = "https://photon.komoot.io/api/"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GOOGLE_MAPS_API_KEY
        self.headers = {"User-Agent": DEFAULT_USER_AGENT}

    def geocode_google(self, query: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None
        params = {
            "query": query,
            "key": self.api_key
        }
        try:
            r = requests.get(self.GOOGLE_PLACES_URL, params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                if results:
                    top = results[0]
                    loc = top.get("geometry", {}).get("location", {})
                    return {
                        "latitude": loc.get("lat"),
                        "longitude": loc.get("lng"),
                        "google_place_id": top.get("place_id"),
                        "formatted_address": top.get("formatted_address"),
                        "engine": "Google Places API"
                    }
        except Exception as e:
            print(f"[Geocoder] Google Places error: {e}")
        return None

    def geocode_osm(self, query: str) -> Optional[Dict[str, Any]]:
        url = f"{self.PHOTON_URL}?q={requests.utils.quote(query)}&limit=1&bbox=68.1,6.5,97.4,35.5"
        try:
            r = requests.get(url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                features = data.get("features", [])
                if features:
                    feat = features[0]
                    coords = feat.get("geometry", {}).get("coordinates", [])
                    props = feat.get("properties", {})
                    if len(coords) >= 2:
                        return {
                            "latitude": round(coords[1], 6),
                            "longitude": round(coords[0], 6),
                            "google_place_id": f"osm:{props.get('osm_type')}:{props.get('osm_id')}",
                            "formatted_address": props.get("name", query),
                            "engine": "OpenStreetMap / Photon Engine"
                        }
        except Exception as e:
            pass
        return None

    def geocode(self, business_name: str, city: str, address: Optional[str] = None) -> Dict[str, Any]:
        query = f"{business_name}, {city}, India"
        
        # 1. Try Google Places API first if key configured
        if self.api_key:
            res = self.geocode_google(query)
            if res:
                return res

        # 2. Seamless fallback to OSM Photon
        osm_res = self.geocode_osm(query)
        if osm_res:
            return osm_res

        # 3. Fallback to city center
        return {
            "latitude": 20.5937,
            "longitude": 78.9629,
            "google_place_id": f"inferred_{abs(hash(query))}",
            "formatted_address": query,
            "engine": "Default Geo Fallback"
        }

