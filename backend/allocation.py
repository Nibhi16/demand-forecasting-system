from __future__ import annotations


def allocate(predicted_demand: float) -> str:
    """
    Translate a demand prediction into a rider-allocation decision.

    Rules:
    - demand > 200  -> "Increase riders"
    - 100 <= demand <= 200 -> "Maintain"
    - demand < 100  -> "Reduce riders"
    """

    demand = float(predicted_demand)
    if demand > 200:
        return "Increase riders"
    if 100 <= demand <= 200:
        return "Maintain"
    return "Reduce riders"

