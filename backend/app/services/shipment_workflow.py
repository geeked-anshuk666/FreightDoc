"""Small, explicit shipment lifecycle for the review-ready product slice.

The workflow is deliberately kept server-side.  A browser may display a state,
but it cannot move a shipment to a state that the API does not permit.
"""

from __future__ import annotations

from enum import Enum


class ShipmentStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    NEEDS_REVIEW = "needs_review"
    REVIEW_READY = "review_ready"
    ARCHIVED = "archived"


_TRANSITIONS: dict[ShipmentStatus, set[ShipmentStatus]] = {
    ShipmentStatus.DRAFT: {ShipmentStatus.PROCESSING, ShipmentStatus.ARCHIVED},
    ShipmentStatus.PROCESSING: {ShipmentStatus.NEEDS_REVIEW, ShipmentStatus.REVIEW_READY, ShipmentStatus.ARCHIVED},
    ShipmentStatus.NEEDS_REVIEW: {ShipmentStatus.PROCESSING, ShipmentStatus.ARCHIVED},
    ShipmentStatus.REVIEW_READY: {ShipmentStatus.PROCESSING, ShipmentStatus.ARCHIVED},
    ShipmentStatus.ARCHIVED: set(),
}


def can_transition(current: str, target: str) -> bool:
    """Return whether a transition is allowed without raising for stale rows."""
    try:
        return ShipmentStatus(target) in _TRANSITIONS[ShipmentStatus(current)]
    except ValueError:
        return False


def transition_error(current: str, target: str) -> str | None:
    if current == target:
        return None
    if can_transition(current, target):
        return None
    return f"A shipment cannot move from '{current}' to '{target}'."
