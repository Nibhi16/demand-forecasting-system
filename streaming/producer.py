from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd


def resolve_csv_path(csv_path: str | Path, project_root: Path) -> Path:
    """
    Resolve user-provided CSV path.

    If a relative path is provided, interpret it relative to `project_root` so the
    default `data/processed_orders.csv` works as specified.
    """

    path = Path(csv_path)
    if path.is_absolute():
        return path
    return project_root / path


def load_orders(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV not found: {csv_path}. Expected file at 'data/processed_orders.csv'."
        )

    df = pd.read_csv(csv_path)
    required_cols = ["week", "center_id", "meal_id", "lag_1", "lag_2"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}. "
            f"Found columns: {list(df.columns)[:20]}..."
        )
    return df


def build_payload_from_row(row: Any) -> dict[str, Any]:
    """
    Build the request payload for `/predict`.

    Accepts dict-like inputs so we can use it with both pandas rows and
    `itertuples()`-extracted values.
    """

    lag_1 = row["lag_1"]
    lag_2 = row["lag_2"]
    # Avoid sending invalid JSON literals like NaN.
    if pd.isna(lag_1):
        lag_1 = 0.0
    if pd.isna(lag_2):
        lag_2 = 0.0

    # API schema expects ints for week/center_id/meal_id and floats for lag_1/lag_2.
    return {
        "week": int(row["week"]),
        "center_id": int(row["center_id"]),
        "meal_id": int(row["meal_id"]),
        "lag_1": float(lag_1),
        "lag_2": float(lag_2),
    }


def send_predict_request(url: str, payload: dict[str, Any], timeout_s: float = 5.0) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        url=url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    with urlopen(req, timeout=timeout_s) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def format_predicted_demand(demand: float) -> str:
    # Make output look like the example: 180 instead of 180.0 when applicable.
    if abs(demand - round(demand)) < 1e-9:
        return str(int(round(demand)))
    return f"{demand:.2f}"


def print_decision_block(week: int, center_id: int, predicted_demand: float, allocation_decision: str) -> None:
    print("---------------------------------")
    print(f"Week: {week} | Center: {center_id}")
    print(f"Predicted Demand: {format_predicted_demand(predicted_demand)}")
    print(f"Decision: {allocation_decision}")
    print("---------------------------------")


def main() -> int:
    parser = argparse.ArgumentParser(description="Stream food orders to the demand prediction API.")
    parser.add_argument(
        "--csv",
        default="data/processed_orders.csv",
        help="Path to processed orders CSV (relative to demand-forecasting-system).",
    )
    parser.add_argument("--url", default="http://127.0.0.1:8000/predict", help="Prediction endpoint URL.")
    parser.add_argument("--sleep-seconds", type=float, default=1.0, help="Delay between requests.")
    parser.add_argument("--timeout-seconds", type=float, default=5.0, help="Per-request timeout.")
    parser.add_argument("--max-rows", type=int, default=0, help="Limit number of rows (0 = no limit).")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]  # demand-forecasting-system/
    csv_path = resolve_csv_path(args.csv, project_root=project_root)

    try:
        df = load_orders(csv_path)
    except Exception as e:
        print(f"[startup] Failed to load orders: {e}", file=sys.stderr)
        return 1

    total_rows = len(df)
    max_rows = args.max_rows if args.max_rows and args.max_rows > 0 else total_rows
    print(
        f"[startup] Streaming {max_rows}/{total_rows} rows from '{csv_path}' every {args.sleep_seconds:.2f}s "
        f"to {args.url}"
    )

    for idx, row in enumerate(df.itertuples(index=False), start=1):
        if idx > max_rows:
            break

        # itertuples is faster than iterrows; use getattr and map explicitly.
        week = int(getattr(row, "week"))
        center_id = int(getattr(row, "center_id"))
        meal_id = int(getattr(row, "meal_id"))
        lag_1 = float(getattr(row, "lag_1"))
        lag_2 = float(getattr(row, "lag_2"))
        payload = build_payload_from_row(
            {"week": week, "center_id": center_id, "meal_id": meal_id, "lag_1": lag_1, "lag_2": lag_2}
        )

        started = time.perf_counter()
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            resp = send_predict_request(args.url, payload=payload, timeout_s=args.timeout_seconds)
            predicted_demand = float(resp["predicted_demand"])
            allocation_decision = str(resp["allocation_decision"])
            print(f"[{ts}] Request #{idx} OK")
            print_decision_block(week=week, center_id=center_id, predicted_demand=predicted_demand, allocation_decision=allocation_decision)
        except HTTPError as e:
            # HTTPError includes status code and often a response body.
            status = getattr(e, "code", "unknown")
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")
            except Exception:
                body = ""
            print(f"[{ts}] Request #{idx} FAILED (HTTP {status}): {body or e}", file=sys.stderr)
        except URLError as e:
            print(f"[{ts}] Request #{idx} FAILED (network): {e}", file=sys.stderr)
        except Exception as e:
            print(f"[{ts}] Request #{idx} FAILED: {e}", file=sys.stderr)

        elapsed = time.perf_counter() - started
        sleep_for = max(0.0, args.sleep_seconds - elapsed)
        time.sleep(sleep_for)

    print("[done] Streaming complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
