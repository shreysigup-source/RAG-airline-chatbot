from __future__ import annotations

from app.services.baggage_service import get_baggage_allowance


def maybe_answer_from_services(question: str) -> str | None:
    """Return a direct answer for common policy questions before falling back to RAG."""

    normalized = question.lower()

    if "baggage" in normalized and "allowance" in normalized:
        result = get_baggage_allowance("economy", "international")
        if result.get("success"):
            data = result["data"]
            return (
                "Baggage allowance depends on your fare and route. "
                f"For a typical economy international itinerary, you usually get {data['cabin_baggage']['pieces']} cabin bag(s) "
                f"up to {data['cabin_baggage']['max_weight_kg']} kg each and {data['checked_baggage']['pieces']} checked bag(s) "
                f"up to {data['checked_baggage']['max_weight_per_piece_kg']} kg each. "
                "If you share your cabin class and route, I can give the exact allowance."
            )

    if "meal" in normalized and ("option" in normalized or "meal" in normalized):
        return (
            "Meal options commonly include standard meals, special meals, pre-order meals, "
            "buy-on-board items, and infant or child meals. Availability depends on your route, cabin, and booking timing."
        )

    return None
