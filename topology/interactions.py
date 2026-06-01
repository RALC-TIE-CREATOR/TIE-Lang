from __future__ import annotations

from .loops import ClosedLoop


def classify_interaction(
    left: ClosedLoop,
    right: ClosedLoop,
    near_threshold: float = 3.0,
) -> str:
    distance = left.distance_to(right)
    if distance > near_threshold:
        return "coexist"

    if left.winding == 0 or right.winding == 0:
        return "coexist"

    if left.winding == -right.winding:
        return "annihilate"

    return "repel"


def apply_local_interaction(
    left: ClosedLoop,
    right: ClosedLoop,
    near_threshold: float = 3.0,
) -> dict:
    action = classify_interaction(left, right, near_threshold=near_threshold)

    if action == "annihilate":
        return {
            "action": action,
            "loops": [],
            "charge_before": left.winding + right.winding,
            "charge_after": 0,
        }

    if action == "repel":
        moved_left = left.translated(dx=-1)
        moved_right = right.translated(dx=1)
        return {
            "action": action,
            "loops": [moved_left, moved_right],
            "charge_before": left.winding + right.winding,
            "charge_after": moved_left.winding + moved_right.winding,
        }

    return {
        "action": action,
        "loops": [left, right],
        "charge_before": left.winding + right.winding,
        "charge_after": left.winding + right.winding,
    }
