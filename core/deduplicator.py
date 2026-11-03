import re
from typing import Optional, Tuple
import math

class EntityCleaner:
    @staticmethod
    def clean_name(name: str) -> str:
        if not name:
            return ""
        name = re.sub(r'\[\d+\]', '', name) # remove wiki citations [1], [2]
        name = re.sub(r'\s+', ' ', name)
        name = name.strip(" \"',.-")
        return name

    @staticmethod
    def clean_phone(phone: Optional[str]) -> Optional[str]:
        if not phone:
            return None
        # Clean non-digit characters except +
        digits = re.sub(r'[^\d+]', '', phone)
        if not digits:
            return None
        
        # If Indian 10 digits without +91, format to +91
        raw_digits = re.sub(r'\D', '', digits)
        if len(raw_digits) == 10:
            return f"+91 {raw_digits[:5]} {raw_digits[5:]}"
        elif len(raw_digits) == 12 and raw_digits.startswith('91'):
            return f"+91 {raw_digits[2:7]} {raw_digits[7:]}"
        elif digits.startswith('+'):
            return digits
        return f"+91 {raw_digits[-10:-5]} {raw_digits[-5:]}" if len(raw_digits) >= 10 else phone

    @staticmethod
    def extract_pin(address: str, default_pin: Optional[str] = None) -> Optional[str]:
        if not address:
            return default_pin
        match = re.search(r'\b([1-9][0-9]{5})\b', address)
        if match:
            return match.group(1)
        return default_pin

    @staticmethod
    def clean_url(url: Optional[str]) -> Optional[str]:
        if not url:
            return None
        url = url.strip()
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        return url

    @staticmethod
    def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates distance between two coordinates in meters."""
        R = 6371000  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2.0) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def get_dedup_key(name: str, city: str) -> str:
        """Normalized deduplication key."""
        clean_n = re.sub(r'[^a-z0-9]', '', name.lower())
        clean_c = re.sub(r'[^a-z0-9]', '', city.lower())
        return f"{clean_n}::{clean_c}"

