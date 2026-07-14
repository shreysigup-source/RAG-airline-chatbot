"""Baggage policy and quotation service for the mock airline backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class BaggagePolicy:
    cabin_pieces: int
    cabin_weight_kg: int
    checked_pieces: int
    checked_weight_kg: int
    infant_checked_kg: int


_POLICIES = {
    "economy": BaggagePolicy(1, 7, 1, 23, 10),
    "premium_economy": BaggagePolicy(1, 10, 2, 23, 10),
    "business": BaggagePolicy(2, 10, 2, 32, 15),
    "first": BaggagePolicy(2, 10, 3, 32, 15),
}
_ROUTE_BANDS = {"domestic": 18.0, "regional": 28.0, "international": 42.0}


def _result(success: bool, message: str, data: Any = None) -> dict[str, Any]:
    return {"success": success, "message": message, "data": data}


def _policy(cabin_class: str) -> Optional[BaggagePolicy]:
    return _POLICIES.get(cabin_class.strip().lower().replace(" ", "_"))


def get_baggage_allowance(
    cabin_class: str, route_type: str = "international", is_infant: bool = False
) -> dict[str, Any]:
    """Return checked and cabin baggage entitlement for a fare cabin."""
    policy = _policy(cabin_class)
    if policy is None or route_type.lower() not in _ROUTE_BANDS:
        return _result(False, "Unsupported cabin class or route type.")
    checked_pieces = policy.checked_pieces + (1 if route_type.lower() == "international" and cabin_class.lower() in {"business", "first"} else 0)
    return _result(True, "Baggage allowance found.", {
        "cabin_baggage": {"pieces": policy.cabin_pieces, "max_weight_kg": policy.cabin_weight_kg,
                           "max_dimensions_cm": "55 x 35 x 25", "personal_item_allowed": True},
        "checked_baggage": {"pieces": checked_pieces, "max_weight_per_piece_kg": policy.checked_weight_kg,
                            "max_linear_dimensions_cm": 158},
        "infant_allowance": {"checked_baggage_kg": policy.infant_checked_kg, "stroller_or_car_seat": True} if is_infant else None,
        "route_type": route_type.lower(),
    })


def calculate_excess_baggage_fee(
    cabin_class: str, route_type: str, bags: int, total_weight_kg: float
) -> dict[str, Any]:
    """Quote excess charges using a transparent mock per-kilogram schedule."""
    if bags < 0 or total_weight_kg < 0:
        return _result(False, "Bag count and weight must be non-negative.")
    policy = _policy(cabin_class)
    rate = _ROUTE_BANDS.get(route_type.lower())
    if policy is None or rate is None:
        return _result(False, "Unsupported cabin class or route type.")
    entitled_weight = policy.checked_pieces * policy.checked_weight_kg
    extra_bags = max(0, bags - policy.checked_pieces)
    excess_weight = max(0.0, total_weight_kg - entitled_weight)
    extra_bag_fee = extra_bags * rate * policy.checked_weight_kg
    overweight_fee = excess_weight * rate
    return _result(True, "Excess baggage quote calculated.", {
        "currency": "USD", "included_weight_kg": entitled_weight, "excess_weight_kg": round(excess_weight, 1),
        "extra_bags": extra_bags, "extra_bag_fee": round(extra_bag_fee, 2),
        "overweight_fee": round(overweight_fee, 2), "total_fee": round(extra_bag_fee + overweight_fee, 2),
        "note": "Charges are estimates and may vary by airport and payment time.",
    })


def get_special_baggage_guidance(item_type: str, weight_kg: float = 0) -> dict[str, Any]:
    """Return handling and acceptance guidance for special items and dangerous goods."""
    if weight_kg < 0:
        return _result(False, "Weight cannot be negative.")
    item = item_type.strip().lower().replace("-", " ")
    guidance = {
        "sports equipment": ("Accepted as checked baggage when packed in a protective case.", "Advance reservation is recommended; standard oversize fees may apply."),
        "musical instrument": ("Small instruments may travel in the cabin if they fit safely.", "Larger instruments require a purchased seat or checked handling case."),
        "oversized baggage": ("Items over 158 cm linear dimensions require special handling.", "Maximum accepted weight is 32 kg per item without cargo approval."),
        "wheelchair": ("Mobility aids are carried without charge.", "Notify the airline at least 48 hours before departure for battery-powered devices."),
        "dangerous goods": ("Spare lithium batteries must travel in cabin baggage with protected terminals.", "Fuel, fireworks, corrosives, and compressed gas cylinders are prohibited unless specifically approved."),
        "pet": ("Pet travel is subject to route, breed, and cabin-space restrictions.", "Contact reservations before ticketing; an approved ventilated carrier is required."),
    }.get(item)
    if guidance is None:
        return _result(False, "Unknown special baggage category.")
    return _result(True, "Special baggage guidance found.", {"item_type": item, "weight_kg": weight_kg, "guidance": guidance[0], "restrictions": guidance[1]})


def purchase_extra_baggage(route_type: str, additional_weight_kg: float) -> dict[str, Any]:
    """Create a mock pre-purchase quote for additional checked baggage weight."""
    rate = _ROUTE_BANDS.get(route_type.lower())
    if rate is None or additional_weight_kg <= 0:
        return _result(False, "Provide a supported route type and positive additional weight.")
    if additional_weight_kg > 69:
        return _result(False, "Online purchase is limited to 69 kg; contact cargo services for larger loads.")
    fee = additional_weight_kg * rate * 0.8
    return _result(True, "Pre-purchase baggage quote created.", {"route_type": route_type.lower(), "additional_weight_kg": additional_weight_kg, "currency": "USD", "price": round(fee, 2), "saving_note": "Pre-purchased baggage is discounted against airport pricing."})