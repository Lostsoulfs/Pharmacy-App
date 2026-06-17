"""Source and review metadata for bundled training datasets.

This module is metadata only. It does not validate the bundled clinical,
law, vaccine, or TPR content and it must not be used to clear the
UNVERIFIED UI banner. `config.DATA_VERIFIED` remains the banner source of
truth until a qualified pharmacist signs a dated audit artifact.
"""

from __future__ import annotations

from collections.abc import Sized
from typing import cast

from pharmacy_app import clinical_data
from pharmacy_app.config import DATA_VERIFIED

UNVERIFIED = "UNVERIFIED"
SOURCE_MAPPED = "SOURCE_MAPPED"
PHARMACIST_SIGNED = "PHARMACIST_SIGNED"

REVIEW_STATUSES = frozenset({
    UNVERIFIED,
    SOURCE_MAPPED,
    PHARMACIST_SIGNED,
})

PTCE_DOMAINS = frozenset({
    "Medications",
    "Federal Requirements",
    "Patient Safety and Quality Assurance",
    "Order Entry and Processing",
})

DATASET_OBJECTS: dict[str, Sized] = {
    "brand_generic": clinical_data.BRAND_GENERIC,
    "red_flags": clinical_data.RED_FLAGS,
    "lasa_pairs": clinical_data.LASA_PAIRS,
    "sig_abbreviations": clinical_data.SIG_ABBREVIATIONS,
    "common_rx_flags": clinical_data.COMMON_RX_FLAGS,
    "vaccines": clinical_data.VACCINES,
    "law": clinical_data.LAW_BULLETS,
    "tpr": clinical_data.TPR_CODES,
}

DATASET_SOURCE_REGISTRY: dict[str, dict[str, object]] = {
    "brand_generic": {
        "review_status": UNVERIFIED,
        "source_ids": (
            "SRC-PTCB-2026-PTCE",
            "SRC-PTCB-2026-KNOWLEDGE",
        ),
        "ptce_domains": ("Medications",),
        "app_area": "Quiz training, drug lookup",
        "source_reviewed_on": "2026-06-17",
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Dataset-level routing only; rows remain unverified.",
    },
    "red_flags": {
        "review_status": UNVERIFIED,
        "source_ids": (
            "SRC-PTCB-2026-PTCE",
            "SRC-FDA-DRUG-SAFETY",
            "SRC-DEA-PHARMACIST-MANUAL",
        ),
        "ptce_domains": (
            "Medications",
            "Patient Safety and Quality Assurance",
            "Federal Requirements",
        ),
        "app_area": "Quiz training, safety prompts",
        "source_reviewed_on": "2026-06-17",
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Dataset-level routing only; scenarios remain unverified.",
    },
    "lasa_pairs": {
        "review_status": UNVERIFIED,
        "source_ids": (
            "SRC-PTCB-2026-PTCE",
            "SRC-PTCB-2026-KNOWLEDGE",
        ),
        "ptce_domains": (
            "Patient Safety and Quality Assurance",
            "Medications",
        ),
        "app_area": "Quiz training",
        "source_reviewed_on": "2026-06-17",
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Dataset-level routing only; pairs remain unverified.",
    },
    "sig_abbreviations": {
        "review_status": UNVERIFIED,
        "source_ids": (
            "SRC-PTCB-2026-PTCE",
            "SRC-PTCB-2026-KNOWLEDGE",
        ),
        "ptce_domains": ("Order Entry and Processing",),
        "app_area": "SIG decoder",
        "source_reviewed_on": "2026-06-17",
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Dataset-level routing only; meanings remain unverified.",
    },
    "common_rx_flags": {
        "review_status": UNVERIFIED,
        "source_ids": (
            "SRC-PTCB-2026-PTCE",
            "SRC-FDA-DRUG-SAFETY",
        ),
        "ptce_domains": (
            "Medications",
            "Patient Safety and Quality Assurance",
        ),
        "app_area": "Drug lookup, warning notes",
        "source_reviewed_on": "2026-06-17",
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Dataset-level routing only; warnings remain unverified.",
    },
    "vaccines": {
        "review_status": UNVERIFIED,
        "source_ids": (
            "SRC-CDC-VACCINE-SCHEDULES",
            "SRC-PTCB-2026-PTCE",
        ),
        "ptce_domains": (
            "Medications",
            "Federal Requirements",
        ),
        "app_area": "Vaccine eligibility panel",
        "source_reviewed_on": "2026-06-17",
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Dataset-level routing only; schedules remain unverified.",
    },
    "law": {
        "review_status": UNVERIFIED,
        "source_ids": (
            "SRC-DEA-PHARMACIST-MANUAL",
            "SRC-DEA-CSA",
            "SRC-PTCB-2026-PTCE",
        ),
        "ptce_domains": ("Federal Requirements",),
        "app_area": "Law panel",
        "source_reviewed_on": "2026-06-17",
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Federal/PTCB routing only; law items remain unverified.",
    },
    "tpr": {
        "review_status": UNVERIFIED,
        "source_ids": (
            "SRC-PTCB-2026-PTCE",
            "SRC-PTCB-2026-KNOWLEDGE",
        ),
        "ptce_domains": (
            "Order Entry and Processing",
            "Patient Safety and Quality Assurance",
        ),
        "app_area": "TPR insurance guide",
        "source_reviewed_on": "2026-06-17",
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Workflow training only; payer-specific facts remain unverified.",
    },
}

COMMON_RX_FLAG_ITEM_REVIEWS: dict[str, dict[str, object]] = {
    "warfarin": {
        "review_status": UNVERIFIED,
        "source_ids": ("SRC-FDA-DRUG-SAFETY", "SRC-PTCB-2026-PTCE"),
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Warning text unchanged; needs qualified review.",
    },
    "methotrexate": {
        "review_status": UNVERIFIED,
        "source_ids": ("SRC-FDA-DRUG-SAFETY", "SRC-PTCB-2026-PTCE"),
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Warning text unchanged; needs qualified review.",
    },
    "insulin": {
        "review_status": UNVERIFIED,
        "source_ids": ("SRC-FDA-DRUG-SAFETY", "SRC-PTCB-2026-PTCE"),
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Warning text unchanged; needs qualified review.",
    },
    "levothyroxine": {
        "review_status": UNVERIFIED,
        "source_ids": ("SRC-FDA-DRUG-SAFETY", "SRC-PTCB-2026-PTCE"),
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Warning text unchanged; needs qualified review.",
    },
    "tramadol": {
        "review_status": UNVERIFIED,
        "source_ids": (
            "SRC-FDA-DRUG-SAFETY",
            "SRC-DEA-PHARMACIST-MANUAL",
            "SRC-PTCB-2026-PTCE",
        ),
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Warning text unchanged; needs qualified review.",
    },
    "alprazolam": {
        "review_status": UNVERIFIED,
        "source_ids": (
            "SRC-FDA-DRUG-SAFETY",
            "SRC-DEA-PHARMACIST-MANUAL",
            "SRC-PTCB-2026-PTCE",
        ),
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Warning text unchanged; needs qualified review.",
    },
    "amoxicillin": {
        "review_status": UNVERIFIED,
        "source_ids": ("SRC-FDA-DRUG-SAFETY", "SRC-PTCB-2026-PTCE"),
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Warning text unchanged; needs qualified review.",
    },
}

SIG_ABBREVIATION_ITEM_KEYS = (
    "QD",
    "QDAY",
    "BID",
    "TID",
    "QID",
    "QHS",
    "QAM",
    "QPM",
    "PRN",
    "PO",
    "SL",
    "TOP",
    "OU",
    "OD",
    "OS",
    "AU",
    "AD",
    "AS",
    "AC",
    "PC",
    "Q4H",
    "Q6H",
    "Q8H",
    "Q12H",
    "UD",
    "AAA",
    "NTE",
)

SIG_ABBREVIATION_ITEM_REVIEWS: dict[str, dict[str, object]] = {
    key: {
        "review_status": UNVERIFIED,
        "source_ids": ("SRC-PTCB-2026-PTCE", "SRC-PTCB-2026-KNOWLEDGE"),
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Meaning text unchanged; needs qualified review.",
    }
    for key in SIG_ABBREVIATION_ITEM_KEYS
}

LASA_PAIR_ITEM_KEYS = (
    "Look-Alike: Hydroxyzine vs Hydralazine. Which is for Itching?",
    "Sound-Alike: Humalog vs Humulin. Which is rapid-acting?",
    "Look-Alike: Zyrtec vs Zyprexa. Which is for allergies?",
    "Look-Alike: Celebrex vs Celexa. Which treats arthritis pain?",
    "Sound-Alike: Klonopin vs Clonidine. Which treats seizures and anxiety?",
    "Look-Alike: Lamictal vs Lamisil. Which treats seizures?",
    "Sound-Alike: Tramadol vs Trazodone. Which is a pain reliever?",
    "Sound-Alike: Bupropion vs Buspirone. Which is used for smoking cessation?",
    "Sound-Alike: Novolog vs Novolin. Which is rapid-acting?",
    "Look-Alike: Lantus vs Latuda. Which is a long-acting insulin?",
    "Look-Alike: Plavix vs Paxil. Which is a blood thinner?",
    "Sound-Alike: Zantac vs Xanax. Which treats heartburn?",
    "Look-Alike: Diflucan vs Diprivan. Which is an antifungal?",
    "Sound-Alike: Cyclobenzaprine vs Cyproheptadine. Which is a muscle relaxant?",
)

LASA_PAIR_ITEM_REVIEWS: dict[str, dict[str, object]] = {
    key: {
        "review_status": UNVERIFIED,
        "source_ids": ("SRC-PTCB-2026-PTCE", "SRC-PTCB-2026-KNOWLEDGE"),
        "item_reviewed_on": None,
        "pharmacist_signoff": None,
        "scope_note": "Question and answer text unchanged; needs qualified review.",
    }
    for key in LASA_PAIR_ITEM_KEYS
}


def registry_entry(dataset_key: str) -> dict[str, object]:
    """Return metadata for a known dataset key."""
    return DATASET_SOURCE_REGISTRY[dataset_key]


def dataset_review_status(dataset_key: str) -> str:
    """Return the review status, failing safe for unknown keys."""
    entry = DATASET_SOURCE_REGISTRY.get(dataset_key)
    if entry is None:
        return UNVERIFIED
    return cast(str, entry["review_status"])


def dataset_source_ids(dataset_key: str) -> tuple[str, ...]:
    """Return candidate source IDs for a known dataset key."""
    entry = DATASET_SOURCE_REGISTRY.get(dataset_key)
    if entry is None:
        return ()
    return tuple(cast(tuple[str, ...], entry["source_ids"]))


def dataset_item_count(dataset_key: str) -> int:
    """Return the current item count for a known dataset key."""
    return len(DATASET_OBJECTS[dataset_key])


def unverified_dataset_keys() -> tuple[str, ...]:
    """Return dataset keys whose visible app banner must remain active."""
    return tuple(key for key, value in DATA_VERIFIED.items() if not value)


def common_rx_flag_item_review(drug_key: str) -> dict[str, object]:
    """Return item-level common RX flag metadata, failing safe."""
    return COMMON_RX_FLAG_ITEM_REVIEWS.get(
        drug_key,
        {
            "review_status": UNVERIFIED,
            "source_ids": (),
            "item_reviewed_on": None,
            "pharmacist_signoff": None,
            "scope_note": "Unknown common RX flag item; treat as unverified.",
        },
    )


def sig_abbreviation_item_review(abbreviation: str) -> dict[str, object]:
    """Return item-level SIG abbreviation metadata, failing safe."""
    return SIG_ABBREVIATION_ITEM_REVIEWS.get(
        abbreviation,
        {
            "review_status": UNVERIFIED,
            "source_ids": (),
            "item_reviewed_on": None,
            "pharmacist_signoff": None,
            "scope_note": "Unknown SIG abbreviation item; treat as unverified.",
        },
    )


def lasa_pair_item_review(question: str) -> dict[str, object]:
    """Return item-level LASA pair metadata, failing safe."""
    return LASA_PAIR_ITEM_REVIEWS.get(
        question,
        {
            "review_status": UNVERIFIED,
            "source_ids": (),
            "item_reviewed_on": None,
            "pharmacist_signoff": None,
            "scope_note": "Unknown LASA pair item; treat as unverified.",
        },
    )
