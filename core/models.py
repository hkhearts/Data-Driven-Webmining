from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class CommercialProperty(BaseModel):
    # Set 1: Discovery-Driven Web Mining Fields
    id: str = Field(..., description="Unique Property Identifier (e.g. IND-PROP-00001)")
    business_name: str = Field(..., description="Clean Commercial Business Name")
    category: str = Field(..., description="Target Category: 5-Star Hotel, 4-Star Hotel, 3-Star Hotel, Resort, Shopping Mall, Marriage / Convention Hall")
    sub_category: Optional[str] = Field(None, description="Granular Classification (e.g. Luxury Heritage Resort, Regional Mall, Kalyana Mandapam)")
    address: str = Field(..., description="Street & Area Address")
    city: str = Field(..., description="City or Town")
    state: str = Field(..., description="State or Union Territory")
    postal_code: Optional[str] = Field(None, description="6-digit Indian PIN Code")
    phone_number: Optional[str] = Field(None, description="Contact Phone with Country Code (+91)")
    website_url: Optional[str] = Field(None, description="Official Website URL or Verified Web Directory Listing")
    source: str = Field(..., description="Web Mining Origin (MakeMyTrip, Wikipedia, NIDHI, Brand Directory, OSM)")

    # Set 2: Geospatial Mapping & Asset Metadata Fields
    latitude: float = Field(..., description="WGS84 Latitude")
    longitude: float = Field(..., description="WGS84 Longitude")
    google_place_id: Optional[str] = Field(None, description="Google Maps Place ID or OSM Unique Feature ID")
    building_polygon: Optional[Dict[str, Any]] = Field(None, description="Vector Structural Footprint Polygon (GeoJSON)")
    building_area_sq_m: float = Field(default=0.0, description="Building Rooftop / Footprint Size in Square Meters")
    building_area_sq_ft: float = Field(default=0.0, description="Building Footprint Size in Square Feet")
    aerial_photo_path: Optional[str] = Field(None, description="Local Disk Path to 600x600 Satellite Aerial Photo")
    aerial_image_url: Optional[str] = Field(None, description="Overhead Satellite Imagery API Request URL")

    # Set 3: Renewable Energy Assessment Fields
    solar_pv_installed: bool = Field(default=False, description="Whether Solar Photovoltaic Panels are Installed")
    solar_pv_confidence: float = Field(default=0.0, description="Computer Vision & Solar API Confidence Score (0.0 to 1.0)")
    solar_panel_estimated_count: int = Field(default=0, description="Estimated Number of PV Modules")
    solar_area_sq_m: float = Field(default=0.0, description="Estimated Solar Array Area in Square Meters")
    
    wind_turbine_installed: bool = Field(default=False, description="Whether Wind Turbines or Captive Wind Energy are Present")
    wind_confidence: float = Field(default=0.0, description="Wind Detection Confidence Score (0.0 to 1.0)")
    wind_evidence: Optional[str] = Field(None, description="Visual / Textual Evidence for Wind Assessment")

    # Metadata & Quality Assurance
    verification_status: str = Field(default="Verified", description="Quality Verification Flag (Verified, Inferred, Geo-Enriched)")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

