"""Tests for dairy_core.data.loader. Hand-made rows only: no Excel file needed."""

from datetime import date

from dairy_core.data.loader import build_stops_by_day, stops_for

D1 = date(2026, 1, 1)
D2 = date(2026, 1, 2)


def row(d, cafe, kg):
    return {"Date": d, "Cafe": cafe, "Quantity (kg)": kg}


def test_case_and_spaces_are_one_cafe():
    rows = [row(D1, "Fire Ice", 5), row(D1, "fire ice ", 3)]
    assert build_stops_by_day(rows) == {D1: ["fire ice"]}


def test_same_cafe_twice_same_day_is_one_stop():
    rows = [row(D1, "Fire Ice", 5), row(D1, "Fire Ice", 7)]
    assert stops_for(build_stops_by_day(rows), D1) == ["fire ice"]


def test_row_with_missing_kg_makes_day_absent():
    rows = [row(D1, "Fire Ice", None)]
    assert build_stops_by_day(rows) == {}


def test_cafe_dash_is_skipped():
    rows = [row(D1, "-", 5), row(D1, "Fire Ice", 5)]
    assert build_stops_by_day(rows) == {D1: ["fire ice"]}


def test_unknown_date_gives_empty_list():
    by_day = build_stops_by_day([row(D1, "Fire Ice", 5)])
    assert stops_for(by_day, D2) == []


def test_two_cafes_keep_file_order():
    rows = [row(D1, "Oasis", 4), row(D1, "Fire Ice", 5)]
    assert stops_for(build_stops_by_day(rows), D1) == ["oasis", "fire ice"]