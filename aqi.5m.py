#!/usr/bin/env python3

# Copyright 2020 John Reese
# Licensed under the MIT License

import json
import logging
import sys
from dataclasses import dataclass
from typing import List, Tuple
from urllib.request import urlopen

SENSOR_IDS = []  # Add local PurpleAir sensor IDs here
PURPLE_JSON_URL = "https://www.purpleair.com/json?show={id}"
PURPLE_MAP_URL = (
    "https://www.purpleair.com/map?opt=1/i/mAQI/a10/cC0&select={id}#11/{lat}/{lon}"
)
STATS_KEYS = ("v", "v1", "v2", "v3")


Series = Tuple[float, ...]

logging.basicConfig(stream=sys.stderr, level=logging.WARNING)


@dataclass
class Result:
    id: int
    name: str
    lat: float
    lon: float
    humidity: float
    stats: List[Series]

def epa_pm(pm: float, humidity: float) -> float:
    # epa adjustment
    logging.info(f"humidity={humidity!r}")
    logging.info(f"pm={pm!r}")
    adjusted = ((0.52 * ((pm + pm) / 2) - (0.085 * humidity) + 5.71))
    logging.info(f"EPA adjustment: {pm:.1f}pm, {humidity:.1f}rh -> {adjusted:.1f}pm")
    return adjusted


def aqi(pm: float, humidity: float) -> int:
    pm = epa_pm(pm, humidity)

    def calc(cp: float, ih: float, il: float, bph: float, bpl: float) -> int:
        a = ih - il
        b = bph - bpl
        c = cp - bpl
        return round((a / b) * c + il)

    if pm < 0 or pm > 1000:
        return pm
    elif pm > 250.5:
        return calc(pm, 400, 301, 350.4, 250.5)
    elif pm > 150.5:
        return calc(pm, 300, 201, 250.4, 150.5)
    elif pm > 55.5:
        return calc(pm, 200, 151, 150.4, 55.5)
    elif pm > 35.5:
        return calc(pm, 150, 101, 55.4, 35.5)
    elif pm > 12.1:
        return calc(pm, 100, 51, 35.4, 12.1)
    else:
        return calc(pm, 50, 0, 12, 0)


def description(aqi: float) -> str:
    if aqi > 300:
        return "☣️  hazardous"
    elif aqi > 200:
        return "🤮 very unhealthy"
    elif aqi > 150:
        return "🤢 unhealthy"
    elif aqi > 100:
        return "😷 unhealthy for sensitive groups"
    elif aqi > 50:
        return "⛅ moderate"
    elif aqi >= 0:
        return "🏖 good"
    else:
        return "🤷‍♀️unknown"


def fetch(sensor_id: int) -> Result:
    response = urlopen(PURPLE_JSON_URL.format(id=sensor_id))
    raw_data = response.read()
    data = json.loads(raw_data)

    stats = []
    for result in data["results"]:
        stat = json.loads(result["Stats"])
        series = tuple(stat[key] for key in STATS_KEYS if key in stat)
        stats.append(series)

    result = data["results"][0]
    return Result(
        id=result["ID"],
        name=result["Label"],
        lat=result["Lat"],
        lon=result["Lon"],
        humidity=float(result["humidity"]),
        stats=stats,
    )

    return result


def combined(result) -> int:
    values = [aqi(pm, result.humidity) for series in result.stats for pm in series[:1]]
    return round(sum(values) / len(values))


def trend(result) -> str:
    values = [aqi(pm, result.humidity) for pm in result.stats[0]]
    avg = sum(values) / len(values)
    latest = values[0]
    dev = abs(avg - latest)
    if dev < 5:
        return " "
    elif latest < avg:
        return "↓"
    elif latest > avg:
        return "↑"
    else:
        return " "


def main():
    if not SENSOR_IDS:
        print("add PurpleAir sensor IDs")
        return

    lines = []
    sensors = []
    values = []
    for sensor_id in SENSOR_IDS:
        result = fetch(sensor_id)
        value = combined(result)
        arrow = trend(result)
        desc = description(value)

        values.append(value)
        lines.append(
            f"{result.name}: {value}{arrow} ({desc.title()})|href={PURPLE_MAP_URL.format(id=result.id, lat=result.lat, lon=result.lon)}"
        )

    avg = round(sum(values) / len(values))
    icon = description(avg).split()[0]
    lines[:0] = [f"AQI: {avg} {icon}", "---"]

    print("\n".join(lines))


if __name__ == "__main__":
    main()
