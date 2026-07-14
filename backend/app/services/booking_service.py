"""Booking management service with realistic in-memory, read-model-style records."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Optional


@dataclass(frozen=True)
class Booking:
    pnr: str; status: str; flight_number: str; passengers: tuple[dict[str, str], ...]; cabin: str; seats: tuple[str, ...]; meals: tuple[str, ...]


_BOOKINGS = (
    Booking("Q7M4KP", "Confirmed", "AR101", ({"name": "Aarav Mehta", "type": "adult"}, {"name": "Nisha Mehta", "type": "adult"}), "economy", ("14A", "14B"), ("Vegetarian", "Standard")),
    Booking("L9R2TX", "Confirmed", "AR305", ({"name": "Maya Iyer", "type": "adult"},), "business", ("3K",), ("Vegan",)),
    Booking("C8W5DN", "Cancelled", "AR204", ({"name": "Rohan Shah", "type": "adult"},), "economy", ("18C",), ("Standard",)),
)


def _result(success: bool, message: str, data: Any = None) -> dict[str, Any]: return {"success": success, "message": message, "data": data}
def _get(pnr: str) -> Optional[Booking]: return next((b for b in _BOOKINGS if b.pnr == pnr.strip().upper()), None)
def _serialize(b: Booking) -> dict[str, Any]: return {"pnr": b.pnr, "status": b.status, "flight_number": b.flight_number, "cabin": b.cabin, "passengers": list(b.passengers), "seats": list(b.seats), "meals": list(b.meals)}


def lookup_booking(pnr: str, last_name: str | None = None) -> dict[str, Any]:
    """Look up a mock booking, optionally validating the lead passenger surname."""
    booking = _get(pnr)
    if booking is None: return _result(False, "Booking reference was not found.")
    if last_name and not booking.passengers[0]["name"].lower().endswith(last_name.strip().lower()): return _result(False, "Booking reference and surname do not match.")
    return _result(True, "Booking found.", _serialize(booking))


def cancel_booking(pnr: str, reason: str | None = None) -> dict[str, Any]:
    """Validate a cancellation request and return the resulting mock outcome.

    The immutable dataset deliberately avoids state changes; an API repository can replace it later.
    """
    booking = _get(pnr)
    if booking is None: return _result(False, "Booking reference was not found.")
    if booking.status == "Cancelled": return _result(False, "This booking is already cancelled.")
    return _result(True, "Cancellation request accepted.", {"pnr": booking.pnr, "previous_status": booking.status, "new_status": "Cancellation requested", "refund_status": "Pending fare-rule assessment", "reason": reason or "Not provided"})


def select_seat(pnr: str, passenger_index: int, seat: str) -> dict[str, Any]:
    """Validate a seat selection against a compact mock seat map."""
    booking = _get(pnr); normalized = seat.strip().upper()
    if booking is None: return _result(False, "Booking reference was not found.")
    if booking.status != "Confirmed": return _result(False, "Seats cannot be changed for this booking status.")
    if not 0 <= passenger_index < len(booking.passengers): return _result(False, "Passenger index is outside this booking.")
    if len(normalized) not in {2, 3} or normalized[-1] not in "ABCDEF" or not normalized[:-1].isdigit(): return _result(False, "Seat must look like 14A.")
    fee = 0.0 if normalized[-1] in "BCDE" else 18.0
    return _result(True, "Seat selection is available.", {"pnr": booking.pnr, "passenger": booking.passengers[passenger_index]["name"], "requested_seat": normalized, "currency": "USD", "fee": fee, "confirmation_required": True})


def select_meal(pnr: str, passenger_index: int, meal: str) -> dict[str, Any]:
    """Validate a special-meal choice for a confirmed booking."""
    allowed = {"standard", "vegetarian", "vegan", "halal", "gluten free", "diabetic"}; booking = _get(pnr)
    if booking is None or not 0 <= passenger_index < len(booking.passengers): return _result(False, "Booking or passenger was not found.")
    if meal.strip().lower() not in allowed: return _result(False, "Unsupported meal. Choose standard, vegetarian, vegan, halal, gluten free, or diabetic.")
    return _result(True, "Meal preference accepted.", {"pnr": booking.pnr, "passenger": booking.passengers[passenger_index]["name"], "meal": meal.strip().title(), "confirmation_required": True})


def request_upgrade(pnr: str, target_cabin: str) -> dict[str, Any]:
    """Quote a mock cabin-upgrade request without mutating the booking."""
    booking = _get(pnr); target = target_cabin.strip().lower().replace(" ", "_")
    prices = {"premium_economy": 160.0, "business": 620.0, "first": 1500.0}
    if booking is None: return _result(False, "Booking reference was not found.")
    if target not in prices or target == booking.cabin: return _result(False, "Requested upgrade cabin is unavailable or unchanged.")
    return _result(True, "Upgrade offer found.", {"pnr": booking.pnr, "from_cabin": booking.cabin, "to_cabin": target, "currency": "USD", "price_per_passenger": prices[target], "availability": "Limited", "confirmation_required": True})