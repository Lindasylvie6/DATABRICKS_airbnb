"""
Pure data-quality classification logic.

This module holds the *rules* that decide whether a booking row is valid,
and if not, which rule it failed. It deliberately contains NO Spark code so
it can be unit-tested in CI (GitHub Actions) without a cluster.

The Silver transform in Databricks applies these same rules at scale via
Spark; this module is the single, testable source of truth for the logic.
"""

ALLOWED_STATUSES = ("confirmed", "cancelled")
MIN_NIGHTS = 1
MAX_NIGHTS = 30


def conform_status(raw_status):
    """Standardize a status value the way the Silver transform does:
    lowercase and strip surrounding whitespace. None stays None."""
    if raw_status is None:
        return None
    return raw_status.strip().lower()


def reject_reason(listing_id, nights, booking_status):
    """
    Classify a single booking row.

    Returns None if the row is valid, otherwise a short string naming the
    first rule it failed. Order of checks is fixed so the reason is
    deterministic when a row breaks more than one rule.
    """
    if listing_id is None:
        return "null_listing_id"

    if nights is None or nights < MIN_NIGHTS or nights > MAX_NIGHTS:
        return "nights_out_of_range"

    if conform_status(booking_status) not in ALLOWED_STATUSES:
        return "invalid_status"

    return None


def is_valid(listing_id, nights, booking_status):
    """Convenience boolean: True when the row passes every rule."""
    return reject_reason(listing_id, nights, booking_status) is None
