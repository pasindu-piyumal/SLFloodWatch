import csv
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from flood.models import Location, FloodRecord, FloodAlert
from flood.risk_levels import score_to_risk_level

BATCH_SIZE = 1000

TRUE_STRINGS = {"yes", "true", "likely", "1"}


def to_bool(value: str) -> bool:
    return str(value).strip().lower() in TRUE_STRINGS


class Command(BaseCommand):
    help = (
        "Imports data/flood_dataset.csv (sri_lanka_flood_risk_dataset) into "
        "the database, creating Location, FloodRecord, and FloodAlert "
        "objects. Run this after migrating, before training the ML model "
        "or using the dashboard."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default=str(settings.FLOOD_DATASET_PATH),
            help="Path to the CSV file to import.",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing Location/FloodRecord/FloodAlert data before importing.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Only import the first N rows (useful for a quick test run).",
        )

    def handle(self, *args, **options):
        path = options["path"]
        limit = options["limit"]

        if options["flush"]:
            FloodAlert.objects.all().delete()
            FloodRecord.objects.all().delete()
            Location.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing flood data."))

        try:
            f = open(path, newline="", encoding="utf-8")
        except FileNotFoundError as exc:
            raise CommandError(f"Could not find dataset at {path}") from exc

        required = {
            "place_name", "district", "latitude", "longitude", "elevation_m",
            "distance_to_river_m", "rainfall_7d_mm", "monthly_rainfall_mm",
            "drainage_index", "flood_risk_score",
        }

        with f:
            reader = csv.DictReader(f)
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise CommandError(f"CSV is missing required columns: {missing}")
            rows = list(reader)

        if limit:
            rows = rows[:limit]

        self.stdout.write(f"Read {len(rows)} rows from {path}. Importing...")

        existing = {
            (loc.name, loc.district): loc
            for loc in Location.objects.all()
        }

        new_locations = []
        latest_row_for_location = {}

        for row in rows:
            key = (row["place_name"].strip(), row["district"].strip())
            row_date = row.get("generation_date", "")
            prev_date = latest_row_for_location.get(key, {}).get("generation_date", "")
            if key not in latest_row_for_location or row_date >= prev_date:
                latest_row_for_location[key] = row

        new_keys = set(latest_row_for_location.keys()) - set(existing.keys())
        for key in new_keys:
            row = latest_row_for_location[key]
            new_locations.append(Location(
                name=row["place_name"].strip(),
                district=row["district"].strip(),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                elevation_m=int(float(row["elevation_m"])),
                distance_to_river_m=float(row["distance_to_river_m"]),
                landcover=row.get("landcover", "").strip(),
                soil_type=row.get("soil_type", "").strip(),
                water_supply=row.get("water_supply", "").strip(),
                electricity=(row.get("electricity") or "").strip(),
                road_quality=row.get("road_quality", "").strip(),
                urban_rural=row.get("urban_rural", "").strip(),
                population_density_per_km2=int(float(row.get("population_density_per_km2", 0))),
                built_up_percent=float(row.get("built_up_percent", 0) or 0),
                infrastructure_score=int(float(row.get("infrastructure_score", 0) or 0)),
                nearest_hospital_km=float(row.get("nearest_hospital_km", 0) or 0),
                nearest_evac_km=float(row.get("nearest_evac_km", 0) or 0),
                is_good_to_live=to_bool(row.get("is_good_to_live", "Yes")),
                reason_not_good_to_live=(row.get("reason_not_good_to_live") or "").strip(),
                current_risk_level=score_to_risk_level(float(row["flood_risk_score"])),
            ))

        with transaction.atomic():
            Location.objects.bulk_create(new_locations, batch_size=BATCH_SIZE)

        # Refresh the lookup now that new locations have PKs
        locations_by_key = {
            (loc.name, loc.district): loc
            for loc in Location.objects.all()
        }

        # Update current_risk_level for locations that already existed
        # (in case this import brings newer data than what's in the DB)
        to_update = []
        for key, row in latest_row_for_location.items():
            loc = locations_by_key.get(key)
            if loc is None:
                continue
            new_risk = score_to_risk_level(float(row["flood_risk_score"]))
            if loc.current_risk_level != new_risk:
                loc.current_risk_level = new_risk
                to_update.append(loc)
        if to_update:
            Location.objects.bulk_update(to_update, ["current_risk_level"], batch_size=BATCH_SIZE)

        # --- Pass 2: create FloodRecord rows in batches -----------------
        existing_record_ids = set(
            FloodRecord.objects.exclude(record_id="").values_list("record_id", flat=True)
        )

        records_to_create = []
        alerts_to_create = []
        created_records = 0

        for row in rows:
            record_id = row.get("record_id", "").strip()
            if record_id and record_id in existing_record_ids:
                continue

            key = (row["place_name"].strip(), row["district"].strip())
            location = locations_by_key.get(key)
            if location is None:
                continue

            score = float(row["flood_risk_score"])
            risk_level = score_to_risk_level(score)
            flood_occurred = to_bool(row.get("flood_occurrence_current_event", "No"))

            try:
                record_date = datetime.strptime(
                    row.get("generation_date", "2024-01-01"), "%Y-%m-%d"
                ).date()
            except ValueError:
                record_date = datetime(2024, 1, 1).date()

            records_to_create.append(FloodRecord(
                location=location,
                record_id=record_id,
                date=record_date,
                rainfall_7d_mm=float(row["rainfall_7d_mm"]),
                monthly_rainfall_mm=float(row["monthly_rainfall_mm"]),
                drainage_index=float(row["drainage_index"]),
                ndvi=float(row.get("ndvi", 0) or 0),
                ndwi=float(row.get("ndwi", 0) or 0),
                water_presence_flag=to_bool(row.get("water_presence_flag", "Unlikely")),
                historical_flood_count=int(float(row.get("historical_flood_count", 0) or 0)),
                flood_risk_score=score,
                risk_level=risk_level,
                flood_occurrence=flood_occurred,
                inundation_area_sqm=int(float(row.get("inundation_area_sqm", 0) or 0)),
            ))
            created_records += 1

            if flood_occurred:
                alerts_to_create.append(FloodAlert(
                    location=location,
                    risk_level=risk_level,
                    message=(
                        f"Active flood event reported — {row.get('inundation_area_sqm', 0)} "
                        f"sqm inundated."
                    ),
                ))
            elif risk_level == "high":
                alerts_to_create.append(FloodAlert(
                    location=location,
                    risk_level=risk_level,
                    message="High flood risk score based on recent rainfall and river data.",
                ))

            if len(records_to_create) >= BATCH_SIZE:
                FloodRecord.objects.bulk_create(records_to_create)
                records_to_create = []

        if records_to_create:
            FloodRecord.objects.bulk_create(records_to_create)

        if alerts_to_create:
            FloodAlert.objects.bulk_create(alerts_to_create, batch_size=BATCH_SIZE)

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {len(new_locations)} new locations, "
                f"{created_records} new flood records, "
                f"{len(alerts_to_create)} alerts generated."
            )
        )
