import argparse
import sys
import time
from pathlib import Path
from typing import List
from tqdm import tqdm

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from scrapers.aggregator import WebMiningAggregator
from geospatial.geocoder import DualEngineGeocoder
from geospatial.building_geometry import BuildingGeometryCalculator
from geospatial.aerial_downloader import AerialSatelliteDownloader
from energy.renewable_pipeline import RenewableAssessmentPipeline
from exports.exporter import DatasetExporter
from core.models import CommercialProperty
from config.settings import GOOGLE_MAPS_API_KEY, DATA_DIR, EXPORTS_DIR

def run_pipeline(
    target_count: int = 10000,
    image_download_limit: int = 150,
    export_prefix: str = "india_commercial_renewable_10k"
):
    start_time = time.time()
    print("=" * 80)
    print(" DISCOVERY-DRIVEN WEB MINING PIPELINE (PAN-INDIA COMMERCIAL DATASET)")
    print(" Set 1: Hotels (3/4/5-Star), Resorts, Malls, Marriage & Convention Halls")
    print(" Set 2: Google Maps / OSM Geocoding, Shapely Polygon Building Footprint Size, Aerial Photos")
    print(" Set 3: Computer Vision Solar PV Module Detection & Wind Turbine / PPA Assessment")
    print(f" Target Volume: {target_count:,} Properties")
    print("=" * 80)

    # -------------------------------------------------------------
    # PHASE 1: SET 1 - MULTI-SOURCE DISCOVERY MINING & EXTRACTION
    # -------------------------------------------------------------
    aggregator = WebMiningAggregator(target_count=target_count)
    
    def on_progress(current, target):
        sys.stdout.write(f"\r[Set 1 Discovery] Harvested: {current:,} / {target:,} commercial venues across India...")
        sys.stdout.flush()

    properties: List[CommercialProperty] = aggregator.run(progress_callback=on_progress)
    print(f"\n[Set 1 Completed] Gathered {len(properties):,} unique commercial records.\n")

    # -------------------------------------------------------------
    # PHASE 2: SET 2 - GEOSPATIAL MAPPING, SHAPELY SIZE & AERIALS
    # -------------------------------------------------------------
    print("-" * 80)
    print("PHASE 2: GEOSPATIAL ASSET METADATA & SHAPELY GEOMETRIC FOOTPRINTS")
    print("-" * 80)
    
    geo_calc = BuildingGeometryCalculator(api_key=GOOGLE_MAPS_API_KEY)
    aerial_downloader = AerialSatelliteDownloader(api_key=GOOGLE_MAPS_API_KEY)
    
    print(f"[Set 2] Fetching aerial satellite imagery concurrently (limit: {image_download_limit} photos)...")
    images_to_download = [
        (p.id, p.latitude, p.longitude) for p in properties[:image_download_limit]
    ]
    downloaded_results = aerial_downloader.download_batch(images_to_download, max_workers=12)

    print("[Set 2] Computing building footprints with Shapely and assigning asset metadata...")
    for idx, prop in enumerate(tqdm(properties, desc="Enriching Geospatial & Building Geometry")):
        poly, m2, ft2 = geo_calc.compute_building_size(
            lat=prop.latitude,
            lon=prop.longitude,
            category=prop.category,
            existing_area_sq_m=prop.building_area_sq_m
        )
        prop.building_polygon = poly
        prop.building_area_sq_m = m2
        prop.building_area_sq_ft = ft2

        if prop.id in downloaded_results:
            local_path, req_url = downloaded_results[prop.id]
            prop.aerial_photo_path = local_path
            prop.aerial_image_url = req_url
        else:
            prop.aerial_image_url = aerial_downloader.get_esri_satellite_url(prop.latitude, prop.longitude)

    # -------------------------------------------------------------
    # PHASE 3: SET 3 - RENEWABLE ENERGY COMPUTER VISION ASSESSMENT
    # -------------------------------------------------------------
    print("-" * 80)
    print("PHASE 3: COMPUTER VISION SOLAR PV & WIND TURBINE ASSESSMENT")
    print("-" * 80)
    
    energy_pipeline = RenewableAssessmentPipeline()
    for prop in tqdm(properties, desc="Running CV Renewable Assessment"):
        energy_pipeline.assess_property(prop)

    # -------------------------------------------------------------
    # PHASE 4: DATASET EXPORTS & ANALYTICS
    # -------------------------------------------------------------
    print("-" * 80)
    print("PHASE 4: EXPORTING CLEAN DATASETS & DASHBOARD DATA")
    print("-" * 80)
    
    exporter = DatasetExporter()
    csv_file = exporter.export_csv(properties, filename=f"{export_prefix}.csv")
    json_file = exporter.export_json(properties, filename=f"{export_prefix}.json")
    geojson_file = exporter.export_geojson(properties, filename=f"{export_prefix}.geojson")
    report = exporter.generate_summary_report(properties, filename=f"{export_prefix}_report.json")

    elapsed = round(time.time() - start_time, 2)
    print("=" * 80)
    print(f" PIPELINE EXECUTION SUCCESSFUL in {elapsed}s")
    print(f" Total Properties Mined: {len(properties):,}")
    print(f" CSV Dataset:     {csv_file}")
    print(f" JSON Dataset:    {json_file}")
    print(f" GeoJSON Dataset: {geojson_file}")
    print(f" Interactive Map: {Path(__file__).parent / 'web' / 'dashboard.html'}")
    print("=" * 80)

    return properties

def main():
    parser = argparse.ArgumentParser(description="Discovery Driven Web Mining Engine (India Commercial Assets & Renewable Assessment)")
    parser.add_argument("--target", type=int, default=10000, help="Target count of commercial properties (default: 10000)")
    parser.add_argument("--images", type=int, default=100, help="Number of satellite aerial images to physically download (default: 100)")
    parser.add_argument("--sample", action="store_true", help="Quick sample run (100 properties)")
    parser.add_argument("--output-prefix", type=str, default="india_commercial_renewable_10k", help="Export file prefix")

    args = parser.parse_args()
    
    target = 100 if args.sample else args.target
    images = min(target, args.images)

    run_pipeline(
        target_count=target,
        image_download_limit=images,
        export_prefix=args.output_prefix
    )

if __name__ == "__main__":
    main()
