from typing import Dict, Any, Optional
from core.models import CommercialProperty
from energy.solar_detector import SolarPVDetector
from energy.wind_detector import WindTurbineDetector

class RenewableAssessmentPipeline:
    def __init__(self):
        self.solar_detector = SolarPVDetector()
        self.wind_detector = WindTurbineDetector()

    def assess_property(self, prop: CommercialProperty) -> CommercialProperty:
        """Runs full Set 3 assessment on the commercial property."""
        # 1. Solar PV Assessment
        solar_res = self.solar_detector.detect(
            image_path=prop.aerial_photo_path,
            building_area_sq_m=prop.building_area_sq_m,
            category=prop.category,
            state=prop.state,
            prop_id=prop.id
        )
        prop.solar_pv_installed = solar_res["solar_pv_installed"]
        prop.solar_pv_confidence = solar_res["solar_pv_confidence"]
        prop.solar_panel_estimated_count = solar_res["solar_panel_estimated_count"]
        prop.solar_area_sq_m = solar_res["solar_area_sq_m"]

        # 2. Wind Energy Assessment
        wind_res = self.wind_detector.assess(
            category=prop.category,
            state=prop.state,
            city=prop.city,
            website_url=prop.website_url,
            image_path=prop.aerial_photo_path,
            business_name=prop.business_name
        )
        prop.wind_turbine_installed = wind_res["wind_turbine_installed"]
        prop.wind_confidence = wind_res["wind_confidence"]
        prop.wind_evidence = wind_res["wind_evidence"]

        return prop

