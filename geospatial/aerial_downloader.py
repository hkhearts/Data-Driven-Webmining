import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Tuple, List, Dict
from config.settings import (
    GOOGLE_MAPS_API_KEY,
    AERIAL_IMAGES_DIR,
    DEFAULT_USER_AGENT,
    REQUEST_TIMEOUT,
    AERIAL_ZOOM_LEVEL,
    AERIAL_IMAGE_SIZE,
    ESRI_SATELLITE_EXPORT_URL
)

class AerialSatelliteDownloader:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GOOGLE_MAPS_API_KEY
        self.headers = {"User-Agent": DEFAULT_USER_AGENT}
        self.output_dir = AERIAL_IMAGES_DIR

    def get_google_static_url(self, lat: float, lon: float, zoom: int = AERIAL_ZOOM_LEVEL) -> str:
        w, h = AERIAL_IMAGE_SIZE
        return (
            f"https://maps.googleapis.com/maps/api/staticmap?"
            f"center={lat},{lon}&zoom={zoom}&size={w}x{h}&maptype=satellite&key={self.api_key}"
        )

    def get_esri_satellite_url(self, lat: float, lon: float) -> str:
        delta = 0.0010
        minx, miny = round(lon - delta, 6), round(lat - delta, 6)
        maxx, maxy = round(lon + delta, 6), round(lat + delta, 6)
        w, h = AERIAL_IMAGE_SIZE
        return (
            f"{ESRI_SATELLITE_EXPORT_URL}?bbox={minx},{miny},{maxx},{maxy}"
            f"&bboxSR=4326&size={w},{h}&imageSR=4326&format=jpg&f=image"
        )

    def download_photo(self, prop_id: str, lat: float, lon: float, timeout: int = 4) -> Tuple[Optional[str], str]:
        filename = f"{prop_id}.jpg"
        dest_path = self.output_dir / filename

        if dest_path.exists() and dest_path.stat().st_size > 1000:
            return str(dest_path), self.get_esri_satellite_url(lat, lon)

        url = self.get_google_static_url(lat, lon) if self.api_key else self.get_esri_satellite_url(lat, lon)

        try:
            r = requests.get(url, headers=self.headers, timeout=timeout)
            if r.status_code == 200 and len(r.content) > 1000:
                with open(dest_path, "wb") as f:
                    f.write(r.content)
                return str(dest_path), url
        except Exception:
            pass

        return None, url

    def download_batch(self, items: List[Tuple[str, float, float]], max_workers: int = 10) -> Dict[str, Tuple[Optional[str], str]]:
        """Downloads satellite photos concurrently using a high-throughput worker pool."""
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {
                executor.submit(self.download_photo, p_id, lat, lon): p_id
                for p_id, lat, lon in items
            }
            for future in as_completed(future_to_id):
                p_id = future_to_id[future]
                try:
                    res = future.result()
                    results[p_id] = res
                except Exception:
                    results[p_id] = (None, self.get_esri_satellite_url(0, 0))
        return results

