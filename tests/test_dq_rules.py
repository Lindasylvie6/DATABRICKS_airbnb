"""
Unit tests for the pure DQ classification logic.

These run in GitHub Actions on every push. They prove the rules that decide
pass-vs-quarantine behave correctly, WITHOUT needing Spark or Databricks.
"""

from src.dq_rules import reject_reason, is_valid, conform_status


# ---- valid rows ----

def test_clean_confirmed_row_passes():
    assert reject_reason(101, 3, "confirmed") is None
    assert is_valid(101, 3, "confirmed") is True


def test_clean_cancelled_row_passes():
    assert reject_reason(202, 14, "cancelled") is None


def test_conforming_fixes_case_and_whitespace():
    # A row that is only "bad" because of casing/spacing must still PASS,
    # because the Silver transform conforms before it judges.
    assert reject_reason(303, 5, "  Confirmed ") is None
    assert conform_status("  Confirmed ") == "confirmed"


# ---- each rule fails as expected ----

def test_null_listing_id_is_caught():
    assert reject_reason(None, 3, "confirmed") == "null_listing_id"


def test_nights_too_high_is_caught():
    assert reject_reason(101, 31, "confirmed") == "nights_out_of_range"


def test_nights_too_low_is_caught():
    assert reject_reason(101, 0, "confirmed") == "nights_out_of_range"


def test_nights_none_is_caught():
    assert reject_reason(101, None, "confirmed") == "nights_out_of_range"


def test_invalid_status_is_caught():
    assert reject_reason(101, 3, "PENDING_REVIEW") == "invalid_status"


# ---- boundary values (the classic off-by-one traps) ----

def test_min_nights_boundary_passes():
    assert reject_reason(101, 1, "confirmed") is None


def test_max_nights_boundary_passes():
    assert reject_reason(101, 30, "confirmed") is None


# ---- fixed precedence when multiple rules fail ----

def test_null_listing_id_takes_precedence_over_status():
    # Row breaks two rules; listing_id is checked first, so that wins.
    assert reject_reason(None, 3, "PENDING_REVIEW") == "null_listing_id"
