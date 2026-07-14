"""Airport directory and proximity lookup service using curated mock data."""

from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Any, Optional


@dataclass(frozen=True)
class Airport:
    code: str; name: str; city: str; country: str; latitude: float; longitude: float; terminals: tuple[str, ...]; contact: str


_AIRPORTS = (
    Airport("DEL", "Indira Gandhi International Airport", "Delhi", "India", 28.5562, 77.1000, ("T1", "T2", "T3"), "+91 11 6123 4567"),
    Airport("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai", "India", 19.0896, 72.8656, ("T1", "T2"), "+91 22 6685 1010"),
    Airport("BLR", "Kempegowda International Airport", "Bengaluru", "India", 13.1986, 77.7066, ("T1", "T2"), "+91 80 6678 2225"),
    Airport("DXB", "Dubai International Airport", "Dubai", "United Arab Emirates", 25.2532, 55.3657, ("T1", "T2", "T3"), "+971 4 224 5555"),
    Airport("LHR", "London Heathrow Airport", "London", "United Kingdom", 51.4700, -0.4543, ("T2", "T3", "T4", "T5"), "+44 20 8745 7777"),
    Airport("SIN", "Singapore Changi Airport", "Singapore", "Singapore", 1.3644, 103.9915, ("T1", "T2", "T3", "T4"), "+65 6595 6868"),
    Airport("JFK", "John F. Kennedy International Airport", "New York", "United States", 40.6413, -73.7781, ("T1", "T4", "T5", "T7", "T8"), "+1 718 244 4444"),
)


def _result(success: bool, message: str, data: Any = None) -> dict[str, Any]: return {"success": success, "message": message, "data": data}
def _find(query: str) -> Optional[Airport]:
    q = query.strip().lower()
    return next((a for a in _AIRPORTS if q in {a.code.lower(), a.city.lower()} or q in a.name.lower()), None)
def _serialize(a: Airport) -> dict[str, Any]:
    return {"code": a.code, "name": a.name, "city": a.city, "country": a.country, "terminals": list(a.terminals), "contact": a.contact,
            "facilities": ["Free Wi-Fi", "ATMs and currency exchange", "Family rooms", "Accessible assistance"], "lounges_available": True}


def lookup_airport(query: str) -> dict[str, Any]:
    """Find an airport by IATA code, city, or part of its name."""
    if not query or not query.strip(): return _result(False, "Airport code, city, or name is required.")
    airport = _find(query)
    return _result(True, "Airport found.", _serialize(airport)) if airport else _result(False, "No airport matched the supplied query.")


def get_airport_terminal(airport_code: str, airline_code: str = "AR") -> dict[str, Any]:
    """Return mock terminal and check-in counter guidance for an airline."""
    airport = _find(airport_code)
    if airport is None or len(airport_code.strip()) != 3: return _result(False, "A valid three-letter airport code is required.")
    terminal = airport.terminals[-1] if airline_code.upper() == "AR" else airport.terminals[0]
    return _result(True, "Terminal information found.", {"airport": airport.code, "airline": airline_code.upper(), "terminal": terminal, "check_in_counters": f"{terminal} counters 40-58", "recommended_arrival": "3 hours before international departure; 2 hours for domestic."})


def find_nearest_airport(latitude: float, longitude: float) -> dict[str, Any]:
    """Find the closest listed airport to geographic coordinates."""
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180: return _result(False, "Latitude or longitude is outside its valid range.")
    def distance(a: Airport) -> float:
        dlat, dlon = radians(a.latitude - latitude), radians(a.longitude - longitude)
        x = sin(dlat / 2) ** 2 + cos(radians(latitude)) * cos(radians(a.latitude)) * sin(dlon / 2) ** 2
        return 6371 * 2 * asin(sqrt(x))
    airport = min(_AIRPORTS, key=distance)
    return _result(True, "Nearest airport found.", {**_serialize(airport), "distance_km": round(distance(airport), 1)})