from __future__ import annotations


def allocate(predicted_demand: float, avg_demand: float) -> str:
    """
    Hybrid allocation logic:
    Uses both relative (avg-based) and absolute thresholds
    to ensure realistic and varied decisions.
    """

    demand = float(predicted_demand)

    # Relative thresholds
    high_relative = avg_demand * 1.10
    low_relative = avg_demand * 0.90

    # Absolute thresholds (to ensure variation)
    high_absolute = 120
    low_absolute = 55

    if demand > high_relative or demand > high_absolute:
        return "Increase riders"

    elif demand < low_relative or demand < low_absolute:
        return "Reduce riders"

    else:
        return "Maintain"