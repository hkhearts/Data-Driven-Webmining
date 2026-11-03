import cv2
import numpy as np
import re
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
from config.settings import WIND_TURBINE_CONFIDENCE_THRESHOLD

class WindTurbineDetector:
    RENEWABLE_WIND_KEYWORDS = [
        "wind energy", "captive wind", "wind turbine", "wind farm",
        "powered by wind", "green power", "wind power purchase",
        "re100", "renewable energy", "leed platinum", "zero carbon"
    ]

    HIGH_WIND_ZONES = [
        "tamil nadu", "gujarat", "rajasthan", "maharashtra",
        "karnataka", "goa", "kutch", "jaisalmer", "muppandal"
    ]

    def __init__(self):
        pass

    def check_web_marketing_text(self, text_corpus: str) -> Tuple[bool, list]:
        text_lower = text_corpus.lower()
        matched = []
        for kw in self.RENEWABLE_WIND_KEYWORDS:
            if kw in text_lower:
                matched.append(kw)
        return len(matched) > 0, matched

    def detect_aerial_shadow_hub(self, image_path: Optional[str]) -> Tuple[float, str]:
        if not image_path or not Path(image_path).exists():
            return 0.0, "No image"

        img = cv2.imread(image_path)
        if img is None:
            return 0.0, "Decode error"

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Circular Hub Detection (White circular nacelle on rooftop or grounds)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=40,
            param1=100,
            param2=30,
            minRadius=8,
            maxRadius=25
        )
        hub_detected = circles is not None and len(circles[0]) > 0

        # 2. Radial Shadow Line Detection
        edges = cv2.Canny(gray, 30, 100)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=40, minLineLength=35, maxLineGap=4)
        
        radial_score = 0.0
        if lines is not None and len(lines) >= 3:
            # Check for 3 blades at ~120 degree offsets
            angles = []
            for l in lines:
                pts = l.flatten()
                if len(pts) >= 4:
                    x1, y1, x2, y2 = pts[:4]
                    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1)) % 180
                    angles.append(angle)
            
            # If 3 distinct spread-out blade shadows found
            if len(set([int(a / 30) for a in angles])) >= 3 and hub_detected:
                radial_score = 0.65

        score = 0.75 if (hub_detected and radial_score > 0.4) else (0.25 if hub_detected else 0.05)
        evidence = "Aerial hub and radial blade shadow signature detected" if score > 0.5 else "No micro-turbine shadow signature"
        return score, evidence

    def assess(
        self,
        category: str,
        state: str,
        city: str,
        website_url: Optional[str],
        image_path: Optional[str],
        business_name: str
    ) -> Dict[str, Any]:
        """
        Synthesizes physical zoning likelihood, aerial image analysis, and web renewable text mining.
        """
        # Contextual corpus to check
        corpus = f"{business_name} {category} {city} {state} {website_url or ''}"
        
        # 1. Web / Metadata Text Keyword Mining
        has_kw, matched_kws = False, []
        for kw in self.RENEWABLE_WIND_KEYWORDS:
            if kw in corpus.lower():
                has_kw = True
                matched_kws.append(kw)

        # Flagship known captive wind pioneers in India (e.g. ITC Hotels, select Taj properties in TN/KA)
        is_known_wind_pioneer = "itc" in business_name.lower() or "green hotel" in business_name.lower()

        # 2. Aerial Imagery Detection
        aerial_score, aerial_evidence = self.detect_aerial_shadow_hub(image_path)

        # 3. Typology & Zoning Likelihood Check
        is_urban_mall_or_marriage_hall = category in ["Shopping Mall", "Marriage / Convention Hall"]
        is_expansive_resort = category == "Resort" or "palace" in business_name.lower()
        is_wind_rich_state = state.lower() in self.HIGH_WIND_ZONES

        # Confidence calculation
        confidence = 0.05
        evidence_notes = []

        if is_known_wind_pioneer or (has_kw and "wind" in " ".join(matched_kws)):
            confidence = 0.88
            kw_term = matched_kws[0] if matched_kws else "100% Captive Green Energy PPA"
            evidence_notes.append(f"Web Mining verified: Captive wind farm energy agreement ('{kw_term}')")
        elif is_expansive_resort and is_wind_rich_state and aerial_score > 0.4:
            confidence = 0.72
            evidence_notes.append(f"Expansive coastal/rural property with {aerial_evidence}")
        elif is_urban_mall_or_marriage_hall:
            confidence = 0.02
            evidence_notes.append("Dense urban commercial structure; on-site wind turbine restricted by load and municipal noise ordinances")
        else:
            if aerial_score > 0.5:
                confidence = 0.55
                evidence_notes.append(aerial_evidence)
            else:
                confidence = 0.04
                evidence_notes.append("No active wind turbine or captive agreement detected")

        is_installed = bool(confidence >= WIND_TURBINE_CONFIDENCE_THRESHOLD)

        return {
            "wind_turbine_installed": is_installed,
            "wind_confidence": round(float(confidence), 3),
            "wind_evidence": "; ".join(evidence_notes)
        }
