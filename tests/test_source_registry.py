#!/usr/bin/env python3
"""Structural tests for source/review metadata.

These tests verify routing metadata only. They do not certify clinical,
legal, vaccine, or TPR correctness.
"""

import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pharmacy_app.config import DATA_VERIFIED  # noqa: E402
from pharmacy_app import clinical_data  # noqa: E402
from pharmacy_app.source_registry import (  # noqa: E402
    COMMON_RX_FLAG_ITEM_REVIEWS,
    DATASET_SOURCE_REGISTRY,
    PHARMACIST_SIGNED,
    PTCE_DOMAINS,
    REVIEW_STATUSES,
    SIG_ABBREVIATION_ITEM_REVIEWS,
    UNVERIFIED,
    common_rx_flag_item_review,
    dataset_item_count,
    dataset_review_status,
    dataset_source_ids,
    sig_abbreviation_item_review,
    unverified_dataset_keys,
)


def test_registry_keys_match_data_verified_keys():
    assert set(DATASET_SOURCE_REGISTRY) == set(DATA_VERIFIED)


def test_registry_statuses_are_valid_and_unverified():
    for key, entry in DATASET_SOURCE_REGISTRY.items():
        assert entry["review_status"] in REVIEW_STATUSES
        assert entry["review_status"] == UNVERIFIED
        assert DATA_VERIFIED[key] is False
        assert entry["pharmacist_signoff"] is None
        assert entry["item_reviewed_on"] is None


def test_no_pharmacist_signed_without_verified_date():
    for key, entry in DATASET_SOURCE_REGISTRY.items():
        if entry["review_status"] == PHARMACIST_SIGNED:
            assert DATA_VERIFIED[key]


def test_source_ids_and_ptce_domains_are_present():
    for entry in DATASET_SOURCE_REGISTRY.values():
        assert entry["source_ids"]
        assert entry["ptce_domains"]
        assert set(entry["ptce_domains"]) <= PTCE_DOMAINS
        assert entry["source_reviewed_on"] == "2026-06-17"
        assert "unverified" in entry["scope_note"].lower()


def test_dataset_item_counts_match_data_objects():
    assert dataset_item_count("brand_generic") == len(clinical_data.BRAND_GENERIC)
    assert dataset_item_count("red_flags") == len(clinical_data.RED_FLAGS)
    assert dataset_item_count("lasa_pairs") == len(clinical_data.LASA_PAIRS)
    assert dataset_item_count("sig_abbreviations") == len(
        clinical_data.SIG_ABBREVIATIONS
    )
    assert dataset_item_count("common_rx_flags") == len(
        clinical_data.COMMON_RX_FLAGS
    )
    assert dataset_item_count("vaccines") == len(clinical_data.VACCINES)
    assert dataset_item_count("law") == len(clinical_data.LAW_BULLETS)
    assert dataset_item_count("tpr") == len(clinical_data.TPR_CODES)


def test_helper_functions_fail_safe_for_unknown_keys():
    assert dataset_review_status("unknown") == UNVERIFIED
    assert dataset_source_ids("unknown") == ()


def test_unverified_dataset_keys_match_config():
    assert set(unverified_dataset_keys()) == {
        key for key, value in DATA_VERIFIED.items() if not value
    }


def test_common_rx_flag_item_metadata_matches_current_rows():
    row_keys = [drug for drug, _ in clinical_data.COMMON_RX_FLAGS]

    assert len(row_keys) == len(set(row_keys))
    assert set(COMMON_RX_FLAG_ITEM_REVIEWS) == set(row_keys)

    for drug_key in row_keys:
        entry = COMMON_RX_FLAG_ITEM_REVIEWS[drug_key]
        assert entry["review_status"] == UNVERIFIED
        assert entry["source_ids"]
        assert entry["item_reviewed_on"] is None
        assert entry["pharmacist_signoff"] is None
        assert "unchanged" in entry["scope_note"].lower()
        assert "review" in entry["scope_note"].lower()


def test_common_rx_flag_item_review_fails_safe_for_unknown_key():
    entry = common_rx_flag_item_review("unknown")

    assert entry["review_status"] == UNVERIFIED
    assert entry["source_ids"] == ()
    assert entry["item_reviewed_on"] is None
    assert entry["pharmacist_signoff"] is None


def test_sig_abbreviation_item_metadata_matches_current_rows():
    row_keys = list(clinical_data.SIG_ABBREVIATIONS)

    assert len(row_keys) == len(set(row_keys))
    assert set(SIG_ABBREVIATION_ITEM_REVIEWS) == set(row_keys)

    for abbreviation in row_keys:
        entry = SIG_ABBREVIATION_ITEM_REVIEWS[abbreviation]
        assert entry["review_status"] == UNVERIFIED
        assert entry["source_ids"]
        assert entry["item_reviewed_on"] is None
        assert entry["pharmacist_signoff"] is None
        assert "unchanged" in entry["scope_note"].lower()
        assert "review" in entry["scope_note"].lower()


def test_sig_abbreviation_item_review_fails_safe_for_unknown_key():
    entry = sig_abbreviation_item_review("UNKNOWN")

    assert entry["review_status"] == UNVERIFIED
    assert entry["source_ids"] == ()
    assert entry["item_reviewed_on"] is None
    assert entry["pharmacist_signoff"] is None


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
