"""Tests for the earthquake plugin."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from plugins.earthquake import EarthquakePlugin
from src.plugins.base import PluginResult

MANIFEST = json.loads("""
{
    "id": "earthquake",
    "name": "Earthquake Monitor",
    "version": "0.1.0",
    "settings_schema": {
        "type": "object",
        "properties": {
            "enabled": {
                "type": "boolean",
                "title": "Enabled",
                "default": false
            },
            "min_magnitude": {
                "type": "number",
                "title": "Minimum Magnitude",
                "description": "Only show earthquakes at or above this magnitude.",
                "default": 4.0,
                "minimum": 0.0,
                "maximum": 10.0
            },
            "feed": {
                "type": "string",
                "title": "Feed Type",
                "description": "Which USGS feed to use.",
                "enum": [
                    "significant_day",
                    "4.5_day",
                    "2.5_day",
                    "1.0_day"
                ],
                "default": "significant_day"
            },
            "refresh_seconds": {
                "type": "integer",
                "title": "Refresh Interval (seconds)",
                "description": "How often to fetch earthquake data.",
                "default": 300,
                "minimum": 60
            }
        },
        "required": []
    }
}
""")

SAMPLE_RESPONSE = json.loads("""
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "mag": 6.1,
                "place": "50km NE of Tokyo, Japan",
                "time": 1746000000000,
                "updated": 1746000060000,
                "felt": null,
                "cdi": null,
                "mmi": null,
                "alert": null,
                "status": "automatic",
                "type": "earthquake",
                "title": "M 6.1 - 50km NE of Tokyo, Japan"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    139.88,
                    35.95,
                    12.4
                ]
            }
        }
    ]
}
""")


@pytest.fixture
def plugin():
    return EarthquakePlugin(MANIFEST)


@pytest.fixture
def configured_plugin():
    p = EarthquakePlugin(MANIFEST)
    p.config = json.loads("""
{
    "min_magnitude": 4.0,
    "feed": "significant_day"
}
""")
    return p


class TestEarthquakePlugin:

    def test_plugin_id(self, plugin):
        assert plugin.plugin_id == "earthquake"

    def test_manifest_valid(self):
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        with open(manifest_path) as f:
            m = json.load(f)
        for field in ("id", "name", "version"):
            assert field in m

    @patch("plugins.earthquake.requests.get")
    def test_fetch_data_success(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.error is None
        assert result.data is not None
        assert "magnitude" in result.data, "missing variable: magnitude"
        assert "location" in result.data, "missing variable: location"
        assert "depth_km" in result.data, "missing variable: depth_km"
        assert "count" in result.data, "missing variable: count"
        assert "time_ago" in result.data, "missing variable: time_ago"

    @patch("plugins.earthquake.requests.get")
    def test_fetch_data_network_error(self, mock_get, configured_plugin):
        import requests as req_mod
        mock_get.side_effect = req_mod.exceptions.ConnectionError("network down")

        result = configured_plugin.fetch_data()

        assert result.available is False
        assert result.error is not None

    @patch("plugins.earthquake.requests.get")
    def test_fetch_data_bad_json(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("bad json")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is False

