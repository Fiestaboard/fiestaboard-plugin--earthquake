"""Display recent significant earthquakes from the USGS real-time feed."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
import requests

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_day.geojson"
USER_AGENT = "FiestaBoard Earthquake Monitor Plugin (https://github.com/Fiestaboard/fiestaboard-plugin--earthquake)"


class EarthquakePlugin(PluginBase):
    """Earthquake Monitor plugin for FiestaBoard."""

    @property
    def plugin_id(self) -> str:
        return "earthquake"

    def fetch_data(self) -> PluginResult:
        import datetime
        try:
            feed = self.config.get("feed") or "significant_day"
            min_mag = float(self.config.get("min_magnitude") or 4.0)
            url = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{feed}.geojson"

            response = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            features = data.get("features", [])
            filtered = [
                f for f in features
                if f.get("properties", {}).get("mag", 0) >= min_mag
            ]

            if not filtered:
                return PluginResult(
                    available=True,
                    data={
                        "magnitude": 0,
                        "location": "None reported",
                        "depth_km": 0,
                        "count": 0,
                        "time_ago": "N/A",
                    },
                )

            latest = filtered[0]
            props = latest["properties"]
            coords = latest["geometry"]["coordinates"]

            mag = round(float(props.get("mag", 0)), 1)
            location = str(props.get("place", "Unknown"))
            depth_km = round(float(coords[2]), 1) if len(coords) > 2 else 0.0

            # Time ago
            eq_time_ms = props.get("time", 0)
            if eq_time_ms:
                delta = datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(eq_time_ms / 1000)
                hours = int(delta.total_seconds() // 3600)
                minutes = int((delta.total_seconds() % 3600) // 60)
                time_ago = f"{hours}h {minutes}m ago" if hours else f"{minutes}m ago"
            else:
                time_ago = "Unknown"

            return PluginResult(
                available=True,
                data={
                    "magnitude": mag,
                    "location": location,
                    "depth_km": depth_km,
                    "count": len(filtered),
                    "time_ago": time_ago,
                },
            )
        except Exception as e:
            logger.exception("Error fetching earthquake data")
            return PluginResult(available=False, error=str(e))

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        mag = config.get("min_magnitude")
        if mag is not None:
            try:
                mag = float(mag)
                if not (0 <= mag <= 10):
                    errors.append("min_magnitude must be between 0 and 10")
            except (TypeError, ValueError):
                errors.append("min_magnitude must be a number")
        valid_feeds = {"significant_day", "4.5_day", "2.5_day", "1.0_day"}
        feed = config.get("feed", "significant_day")
        if feed not in valid_feeds:
            errors.append(f"feed must be one of: {', '.join(sorted(valid_feeds))}")
        return errors

    def cleanup(self) -> None:
        pass
