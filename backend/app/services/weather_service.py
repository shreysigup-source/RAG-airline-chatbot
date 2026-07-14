"""Destination weather and travel-advisory service using deterministic mock data."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Optional


@dataclass(frozen=True)
class Weather:
    location: str; airport_code: str; temperature_c: int; condition: str; rain_probability: int; wind_kph: int; warning: str | None


_WEATHER = (
    Weather("Delhi", "DEL", 33, "Hazy sunshine", 20, 14, None),
    Weather("Mumbai", "BOM", 29, "Monsoon showers", 75, 24, "Allow extra time for surface travel during heavy rain."),
    Weather("Bengaluru", "BLR", 25, "Cloudy", 45, 16, None),
    Weather("Dubai", "DXB", 41, "Clear and hot", 0, 19, "Heat advisory: stay hydrated before and after travel."),
    Weather("London", "LHR", 19, "Light rain", 65, 27, "Gusty winds may affect airside operations."),
    Weather("Singapore", "SIN", 31, "Thunderstorms nearby", 70, 18, "Brief lightning-related ground holds are possible."),
    Weather("New York", "JFK", 27, "Partly cloudy", 25, 22, None),
)


def _result(success: bool, message: str, data: Any = None) -> dict[str, Any]: return {"success": success, "message": message, "data": data}
def _find(destination: str) -> Optional[Weather]:
    query = destination.strip().lower()
    return next((w for w in _WEATHER if query in {w.location.lower(), w.airport_code.lower()}), None)


def get_destination_weather(destination: str) -> dict[str, Any]:
    """Return current mock conditions and a travel-friendly forecast summary."""
    weather = _find(destination)
    if weather is None: return _result(False, "Weather is unavailable for this destination.")
    data = asdict(weather)
    data["forecast"] = {"next_12_hours": weather.condition, "rain_expected": weather.rain_probability >= 50}
    return _result(True, "Destination weather found.", data)


def get_travel_advisory(destination: str) -> dict[str, Any]:
    """Provide weather-sensitive, practical airport travel precautions."""
    weather = _find(destination)
    if weather is None: return _result(False, "Travel advisory is unavailable for this destination.")
    precautions = ["Check flight status before leaving for the airport.", "Keep essential medication and a charger in cabin baggage."]
    if weather.rain_probability >= 50: precautions.append("Carry rain protection and plan additional ground-transfer time.")
    if weather.temperature_c >= 35: precautions.append("Drink water regularly and avoid leaving electronics in direct heat.")
    if weather.wind_kph >= 25: precautions.append("Expect possible gate or departure-time changes due to wind conditions.")
    return _result(True, "Travel advisory prepared.", {"destination": weather.location, "airport_code": weather.airport_code, "weather_warning": weather.warning, "precautions": precautions, "operational_impact": "Monitor flight notifications." if weather.warning else "No weather-related disruption is currently indicated in this mock feed."})