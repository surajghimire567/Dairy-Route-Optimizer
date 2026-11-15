"""dairy_core.data.loader

Day 2: turn the delivery workbook into "which cafes did we visit on which day".

Rules:
  - skip a row if kg is missing or <= 0
  - skip a row if the cafe is "-" or blank
  - trim spaces and ignore case in cafe names
  - same cafe twice on one day = ONE stop (keep the first row)
  - a day with no valid rows is absent from the result
  - stop order must be deterministic (same input -> same order)

Cafe names in the workbook are already canonical (one name per cafe),
so no alias table is needed here.

Layering: only read_rows() touches Excel. The other functions work on
plain Python data, so tests need no Excel file.
"""

import warnings
from pathlib import Path

from openpyxl import load_workbook

# The workbook has a dropdown on the Cafe column that openpyxl cannot read.
# Reading is unaffected, so hide the warning.
warnings.filterwarnings("ignore", message="Data Validation extension")

SHEET_NAME = "Clean Data"
COL_DATE = "Date"
COL_CAFE = "Cafe"
COL_KG = "Quantity (kg)"


def read_rows(path):
    """Read the "Clean Data" sheet and return a list of dicts, one per row.

    No cleaning here: blanks stay None, names stay as typed.
    """
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb[SHEET_NAME]
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    result = []
    for row in rows:
        result.append(dict(zip(header, row)))
    return result


def normalise_cafe(name):
    """Return the cleaned cafe name, or None if there is no usable cafe."""
    if name is None:
        return None
    cleaned = str(name).strip().lower()      # trim + ignore case
    if cleaned == "" or cleaned == "-":      # blank or "-" = no cafe
        return None
    return cleaned


def is_valid_row(row):
    """Return True if this row should count as a delivery."""
    kg = row.get(COL_KG)
    if kg is None or kg <= 0:
        return False
    return normalise_cafe(row.get(COL_CAFE)) is not None


def build_stops_by_day(rows):
    """Pure logic. Take a list of row dicts, return {date: [cafe, ...]}."""
    by_day = {}
    for row in rows:
        if not is_valid_row(row):
            continue
        date = row.get(COL_DATE)
        if date is None:
            continue
        if hasattr(date, "date"):            # Excel gives datetime; keep date only
            date = date.date()
        cafe = normalise_cafe(row[COL_CAFE])
        stops = by_day.setdefault(date, [])  # day appears only once a valid row exists
        if cafe not in stops:                # first row wins, repeats ignored
            stops.append(cafe)
    return by_day


def stops_for(by_day, date):
    """Return the stops for one date, or [] if that date is not in by_day."""
    return list(by_day.get(date, []))


if __name__ == "__main__":
    # Works from any folder: path is built from this file's location.
    path = Path(__file__).resolve().parents[2] / "data" / "cafe_data.xlsx"
    data = read_rows(path)
    print("rows read:", len(data))
    print("rows kept:", sum(1 for r in data if is_valid_row(r)))
    by_day = build_stops_by_day(data)
    print("days with stops:", len(by_day))
    print("distinct cafes:", len({c for s in by_day.values() for c in s}))
    counts = {}
    for stops in by_day.values():
        counts[len(stops)] = counts.get(len(stops), 0) + 1
    print("stops per day:", dict(sorted(counts.items())))