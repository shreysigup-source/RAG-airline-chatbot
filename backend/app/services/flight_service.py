"""Flight search, timetable, and operational status service backed by mock records."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime, time
from typing import Any, Optional


@dataclass(frozen=True)
class Flight:
    number: str; origin: str; destination: str; departure: str; arrival: str; duration_minutes: int; terminal: str; gate: str; status: str; seats: int; aircraft: str


_FLIGHTS = (
    Flight("AR101", "DEL", "BOM", "2026-07-15T07:30:00+05:30", "2026-07-15T09:40:00+05:30", 130, "T3", "28A", "On Time", 34, "Airbus A320neo"),
    Flight("AR204", "BOM", "DXB", "2026-07-15T11:15:00+05:30", "2026-07-15T13:05:00+04:00", 200, "T2", "C12", "Delayed", 18, "Boeing 737-8"),
    Flight("AR305", "DEL", "LHR", "2026-07-15T02:10:00+05:30", "2026-07-15T07:15:00+01:00", 575, "T3", "12", "On Time", 9, "Boeing 787-9"),
    Flight("AR412", "BLR", "SIN", "2026-07-15T23:40:00+05:30", "2026-07-16T06:55:00+08:00", 285, "T2", "D7", "Boarding", 4, "Airbus A321neo"),
    Flight("AR518", "DXB", "JFK", "2026-07-16T02:05:00+04:00", "2026-07-16T08:30:00-04:00", 985, "T1", "A16", "Scheduled", 22, "Boeing 777-300ER"),
    Flight("AR622", "SIN", "DEL", "2026-07-16T09:20:00+08:00", "2026-07-16T12:35:00+05:30", 345, "T1", "F31", "Scheduled", 41, "Airbus A350-900"),
)


def _result(success: bool, message: str, data: Any = None) -> dict[str, Any]: return {"success": success, "message": message, "data": data}
def _normalize(code: str) -> str: return code.strip().upper()
def _serialize(flight: Flight) -> dict[str, Any]:
    data = asdict(flight)
    data["boarding_time"] = (datetime.fromisoformat(flight.departure).replace(tzinfo=None) - __import__("datetime").timedelta(minutes=45)).isoformat()
    data["duration"] = f"{flight.duration_minutes // 60}h {flight.duration_minutes % 60}m"
    if flight.status == "Delayed": data["delay_minutes"] = 55; data["estimated_departure"] = "2026-07-15T12:10:00+05:30"
    return data


def search_flights(origin: str, destination: str, travel_date: str | None = None, passengers: int = 1) -> dict[str, Any]:
    """Search direct flights and an optional one-stop itinerary in the mock schedule."""
    if passengers < 1 or not origin or not destination or _normalize(origin) == _normalize(destination): return _result(False, "Provide distinct origin and destination codes and at least one passenger.")
    if travel_date:
        try: date.fromisoformat(travel_date)
        except ValueError: return _result(False, "travel_date must use YYYY-MM-DD format.")
    direct = [f for f in _FLIGHTS if f.origin == _normalize(origin) and f.destination == _normalize(destination) and f.seats >= passengers]
    connections = []
    if not direct:
        for first in _FLIGHTS:
            for second in _FLIGHTS:
                if first.origin == _normalize(origin) and first.destination == second.origin and second.destination == _normalize(destination) and min(first.seats, second.seats) >= passengers:
                    connections.append({"segments": [_serialize(first), _serialize(second)], "connection_airport": first.destination, "connection_duration_minutes": 95})
    return _result(True, "Flights found." if direct or connections else "No flights are available for this route.", {"origin": _normalize(origin), "destination": _normalize(destination), "travel_date": travel_date, "direct_flights": [_serialize(f) for f in direct], "connecting_flights": connections})


def get_flight_status(flight_number: str) -> dict[str, Any]:
    """Retrieve real-time-style operational details for a flight number."""
    flight = next((f for f in _FLIGHTS if f.number == _normalize(flight_number)), None)
    return _result(True, "Flight status found.", _serialize(flight)) if flight else _result(False, "Flight number was not found in the current schedule.")


def get_flight_schedule(airport_code: str, direction: str = "departure") -> dict[str, Any]:
    """List scheduled arrivals or departures at an airport."""
    direction = direction.lower()
    if direction not in {"departure", "arrival"}: return _result(False, "direction must be 'departure' or 'arrival'.")
    code = _normalize(airport_code); field = "origin" if direction == "departure" else "destination"
    flights = [f for f in _FLIGHTS if getattr(f, field) == code]
    return _result(True, "Schedule found.", {"airport_code": code, "direction": direction, "flights": [_serialize(f) for f in flights]})


def get_route_information(origin: str, destination: str) -> dict[str, Any]:
    """Return a route summary derived from scheduled flight records."""
    matches = [f for f in _FLIGHTS if f.origin == _normalize(origin) and f.destination == _normalize(destination)]
    if not matches: return _result(False, "No direct route information is available.")
    f = matches[0]
    return _result(True, "Route information found.", {"origin": f.origin, "destination": f.destination, "distance_km_estimate": round(f.duration_minutes * 12.5), "typical_duration": f"{f.duration_minutes // 60}h {f.duration_minutes % 60}m", "aircraft": sorted({x.aircraft for x in matches}), "flights_per_day": len(matches)})