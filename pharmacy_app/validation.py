"""Pure validation helpers for UI-facing text fields.

These helpers do not import tkinter or touch SQLite. They normalize and
bound user input so Tkinter handlers can stay small and behavior can be
tested before wiring panel code through the helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re

MAX_FILTER_LEN = 80
MAX_NAME_LEN = 80
MAX_DRUG_NAME_LEN = 120
MAX_SIG_LEN = 200
MAX_SIG_TOKENS = 40
MAX_SIG_TOKEN_LEN = 16
MAX_QTY_OWED = 999_999

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SIG_TOKEN = re.compile(r"^[A-Z0-9./+-]+$")


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    value: object = None
    error: str = ""


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _has_control_characters(text: str, allow_newlines: bool = False) -> bool:
    allowed = {"\t"}
    if allow_newlines:
        allowed.update({"\n", "\r"})
    return any(ord(ch) < 32 and ch not in allowed for ch in text)


def validate_text_field(
    value: object,
    label: str,
    *,
    max_len: int,
    required: bool = True,
    allow_newlines: bool = False,
) -> ValidationResult:
    text = _clean(value)
    if required and not text:
        return ValidationResult(False, "", f"{label} is required.")
    if len(text) > max_len:
        return ValidationResult(
            False,
            text,
            f"{label} must be {max_len} characters or less.",
        )
    if _has_control_characters(text, allow_newlines=allow_newlines):
        return ValidationResult(
            False,
            text,
            f"{label} contains unsupported control characters.",
        )
    return ValidationResult(True, text, "")


def validate_filter_text(value: object, label: str = "Filter") -> ValidationResult:
    return validate_text_field(
        value,
        label,
        max_len=MAX_FILTER_LEN,
        required=False,
    )


def validate_drug_name(value: object, label: str = "Drug") -> ValidationResult:
    return validate_text_field(value, label, max_len=MAX_DRUG_NAME_LEN)


def validate_person_name(value: object, label: str = "Patient") -> ValidationResult:
    return validate_text_field(value, label, max_len=MAX_NAME_LEN)


def validate_iso_date(value: object, label: str = "Date") -> ValidationResult:
    text_result = validate_text_field(value, label, max_len=10)
    if not text_result.ok:
        return text_result
    text = str(text_result.value)
    if not ISO_DATE.fullmatch(text):
        return ValidationResult(
            False,
            text,
            f"{label} must be YYYY-MM-DD, zero-padded.",
        )
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        return ValidationResult(False, text, f"{label} is not a real date.")
    return ValidationResult(True, text, "")


def validate_positive_int(
    value: object,
    label: str,
    *,
    max_value: int = MAX_QTY_OWED,
) -> ValidationResult:
    text = _clean(value)
    if not text:
        return ValidationResult(False, None, f"{label} is required.")
    if not re.fullmatch(r"\d+", text):
        return ValidationResult(False, None, f"{label} must be a whole number.")
    number = int(text)
    if number <= 0:
        return ValidationResult(False, number, f"{label} must be greater than 0.")
    if number > max_value:
        return ValidationResult(
            False,
            number,
            f"{label} must be {max_value} or less.",
        )
    return ValidationResult(True, number, "")


def validate_lookup_query(value: object) -> ValidationResult:
    result = validate_text_field(
        value,
        "Lookup query",
        max_len=MAX_FILTER_LEN,
    )
    if not result.ok:
        return result
    if len(str(result.value)) < 2:
        return ValidationResult(
            False,
            result.value,
            "Lookup query must be at least 2 characters.",
        )
    return result


def validate_sig_tokens(value: object) -> ValidationResult:
    text_result = validate_text_field(value, "SIG", max_len=MAX_SIG_LEN)
    if not text_result.ok:
        return text_result
    tokens = str(text_result.value).upper().split()
    if len(tokens) > MAX_SIG_TOKENS:
        return ValidationResult(
            False,
            tokens,
            f"SIG must contain {MAX_SIG_TOKENS} tokens or fewer.",
        )
    for token in tokens:
        if len(token) > MAX_SIG_TOKEN_LEN:
            return ValidationResult(
                False,
                tokens,
                f"SIG token '{token}' is too long.",
            )
        if not SIG_TOKEN.fullmatch(token):
            return ValidationResult(
                False,
                tokens,
                f"SIG token '{token}' contains unsupported characters.",
            )
    return ValidationResult(True, tokens, "")


def validate_inventory_entry(drug: object, exp_date: object) -> ValidationResult:
    drug_result = validate_drug_name(drug)
    if not drug_result.ok:
        return drug_result
    date_result = validate_iso_date(exp_date, "Expiration date")
    if not date_result.ok:
        return date_result
    return ValidationResult(
        True,
        {
            "drug": drug_result.value,
            "exp_date": date_result.value,
        },
        "",
    )


def validate_partial_fill(
    drug: object,
    qty_owed: object,
    patient: object,
    date: object,
) -> ValidationResult:
    drug_result = validate_drug_name(drug)
    if not drug_result.ok:
        return drug_result
    qty_result = validate_positive_int(qty_owed, "Qty owed")
    if not qty_result.ok:
        return qty_result
    patient_result = validate_person_name(patient)
    if not patient_result.ok:
        return patient_result
    date_result = validate_iso_date(date)
    if not date_result.ok:
        return date_result
    return ValidationResult(
        True,
        {
            "drug": drug_result.value,
            "qty_owed": qty_result.value,
            "patient": patient_result.value,
            "date": date_result.value,
        },
        "",
    )
