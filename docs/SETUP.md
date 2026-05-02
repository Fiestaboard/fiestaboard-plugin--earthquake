# Earthquake Monitor Setup Guide

Display recent significant earthquakes from the USGS real-time feed.

## Overview

The Earthquake Monitor plugin uses the USGS Earthquake Hazards Program GeoJSON feed to show the most recent significant earthquakes worldwide. Configure a minimum magnitude threshold and an optional radius around a location. No API key required.

- API reference: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

### Prerequisites

No API key or account required.

## Quick Setup

1. **Enable** — Go to **Integrations** in your FiestaBoard settings and enable **Earthquake Monitor**.
2. **Configure** — Fill in the plugin settings (see Configuration Reference below).
3. **Template** — Add a page using the `earthquake` plugin variables:
   ```
   {{{ earthquake.status }}}
   ```
4. **View** — Navigate to your board page to see the live display.

## Template Variables

| Variable | Description | Example |
|---|---|---|
| `earthquake.magnitude` | Magnitude of the most recent earthquake | `6.1` |
| `earthquake.location` | Location description of the most recent earthquake | `50km NE of Tokyo` |
| `earthquake.depth_km` | Focal depth in km | `12.4` |
| `earthquake.count` | Number of earthquakes in the feed | `3` |
| `earthquake.time_ago` | How long ago the most recent quake occurred | `2h ago` |

## Configuration Reference

| Setting | Name | Description | Default |
|---|---|---|---|
| `enabled` | Enabled |  | `False` |
| `min_magnitude` | Minimum Magnitude | Only show earthquakes at or above this magnitude. | `4.0` |
| `feed` | Feed Type | Which USGS feed to use. | `significant_day` |
| `refresh_seconds` | Refresh Interval (seconds) | How often to fetch earthquake data. | `300` |

## Troubleshooting

- **No earthquakes shown** — the feed may have no events above your minimum magnitude.
- **Old data** — try switching to a higher-frequency feed (e.g. `2.5_day`).

