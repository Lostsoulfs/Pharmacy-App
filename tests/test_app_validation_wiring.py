#!/usr/bin/env python3
"""Method-level tests for Tkinter handler validation wiring.

These tests avoid creating a Tk root. They call non-visual handler methods on
an uninitialized PharmacyApp shell with DB and messagebox calls monkeypatched.
"""

import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pharmacy_app.app as appmod  # noqa: E402
from pharmacy_app.app import PharmacyApp  # noqa: E402
from pharmacy_app.validation import MAX_FILTER_LEN  # noqa: E402


def _shell():
    shell = object.__new__(PharmacyApp)
    shell.user = "DefaultAdmin"
    shell._audit_filter = ""
    shell._inv_filter = ""
    shell._partial_edit = None
    shell.nav = []
    shell.navigate_to = lambda route: shell.nav.append(route)
    return shell


def _capture_errors(monkeypatch):
    errors = []
    monkeypatch.setattr(
        appmod.messagebox,
        "showerror",
        lambda title, message: errors.append((title, message)),
    )
    return errors


def _capture_info(monkeypatch):
    messages = []
    monkeypatch.setattr(
        appmod.messagebox,
        "showinfo",
        lambda title, message: messages.append((title, message)),
    )
    return messages


def test_admin_add_inventory_uses_clean_payload(monkeypatch):
    shell = _shell()
    errors = _capture_errors(monkeypatch)
    inventory_calls = []
    audit_calls = []
    monkeypatch.setattr(
        appmod,
        "db_add_inventory",
        lambda drug, exp: inventory_calls.append((drug, exp)),
    )
    monkeypatch.setattr(
        appmod,
        "db_log_audit",
        lambda user, action: audit_calls.append((user, action)),
    )

    PharmacyApp._admin_add_inv(shell, "  Lipitor  ", "2027-03-15")

    assert errors == []
    assert inventory_calls == [("Lipitor", "2027-03-15")]
    assert audit_calls == [
        ("DefaultAdmin", "Inventory add: Lipitor exp 2027-03-15")
    ]
    assert shell.nav == ["admin"]


def test_admin_add_inventory_rejects_bad_date(monkeypatch):
    shell = _shell()
    errors = _capture_errors(monkeypatch)
    inventory_calls = []
    monkeypatch.setattr(
        appmod,
        "db_add_inventory",
        lambda drug, exp: inventory_calls.append((drug, exp)),
    )

    PharmacyApp._admin_add_inv(shell, "Lipitor", "2027-13-01")

    assert inventory_calls == []
    assert errors and errors[0][0] == "Inventory"
    assert shell.nav == []


def test_partial_add_uses_typed_payload(monkeypatch):
    shell = _shell()
    errors = _capture_errors(monkeypatch)
    partial_calls = []
    audit_calls = []
    monkeypatch.setattr(
        appmod,
        "db_add_partial",
        lambda drug, qty, patient, date:
            partial_calls.append((drug, qty, patient, date)),
    )
    monkeypatch.setattr(
        appmod,
        "db_log_audit",
        lambda user, action: audit_calls.append((user, action)),
    )

    PharmacyApp._partial_add(shell, "  Adderall  ", "30", " J. Doe ", "2026-05-20")

    assert errors == []
    assert partial_calls == [("Adderall", 30, "J. Doe", "2026-05-20")]
    assert audit_calls == [
        ("DefaultAdmin", "Logged partial: Adderall for J. Doe")
    ]
    assert shell.nav == ["partials"]


def test_partial_add_rejects_bad_quantity(monkeypatch):
    shell = _shell()
    errors = _capture_errors(monkeypatch)
    partial_calls = []
    monkeypatch.setattr(
        appmod,
        "db_add_partial",
        lambda drug, qty, patient, date:
            partial_calls.append((drug, qty, patient, date)),
    )

    PharmacyApp._partial_add(shell, "Adderall", "0", "J. Doe", "2026-05-20")

    assert partial_calls == []
    assert errors and errors[0][0] == "Partial"
    assert shell.nav == []


def test_partial_prepare_and_cancel_edit_manage_state():
    shell = _shell()
    row = (7, "Adderall", 30, "J. Doe", "2026-05-20")

    PharmacyApp._partial_prepare_edit(shell, row)

    assert shell._partial_edit == row
    assert shell.nav == ["partials"]

    PharmacyApp._partial_cancel_edit(shell)

    assert shell._partial_edit is None
    assert shell.nav == ["partials", "partials"]


def test_partial_update_uses_typed_payload(monkeypatch):
    shell = _shell()
    shell._partial_edit = (7, "Old", 1, "Old Patient", "2026-05-19")
    errors = _capture_errors(monkeypatch)
    update_calls = []
    audit_calls = []
    monkeypatch.setattr(
        appmod,
        "db_update_partial",
        lambda pid, drug, qty, patient, date:
            update_calls.append((pid, drug, qty, patient, date)) or True,
    )
    monkeypatch.setattr(
        appmod,
        "db_log_audit",
        lambda user, action: audit_calls.append((user, action)),
    )

    PharmacyApp._partial_update(
        shell, 7, "  Adderall  ", "30", " J. Doe ", "2026-05-20")

    assert errors == []
    assert update_calls == [(7, "Adderall", 30, "J. Doe", "2026-05-20")]
    assert audit_calls == [
        ("DefaultAdmin", "Edited partial (ID: 7): Adderall for J. Doe")
    ]
    assert shell._partial_edit is None
    assert shell.nav == ["partials"]


def test_partial_update_rejects_bad_payload(monkeypatch):
    shell = _shell()
    errors = _capture_errors(monkeypatch)
    update_calls = []
    monkeypatch.setattr(
        appmod,
        "db_update_partial",
        lambda pid, drug, qty, patient, date:
            update_calls.append((pid, drug, qty, patient, date)) or True,
    )

    PharmacyApp._partial_update(shell, 7, "Adderall", "0", "J. Doe", "2026-05-20")

    assert update_calls == []
    assert errors and errors[0][0] == "Partial"
    assert shell.nav == []


def test_partial_update_reports_stale_row(monkeypatch):
    shell = _shell()
    shell._partial_edit = (7, "Old", 1, "Old Patient", "2026-05-19")
    _capture_errors(monkeypatch)
    messages = _capture_info(monkeypatch)
    monkeypatch.setattr(
        appmod,
        "db_update_partial",
        lambda pid, drug, qty, patient, date: False,
    )

    PharmacyApp._partial_update(
        shell, 7, "Adderall", "30", "J. Doe", "2026-05-20")

    assert messages and messages[0][0] == "Partial"
    assert shell._partial_edit is None
    assert shell.nav == ["partials"]


def test_admin_filters_trim_and_reject_too_long(monkeypatch):
    shell = _shell()
    errors = _capture_errors(monkeypatch)

    PharmacyApp._admin_audit_filter(shell, "  Alice  ")
    PharmacyApp._admin_inv_filter(shell, "  Lipitor  ")
    PharmacyApp._admin_audit_filter(shell, "x" * (MAX_FILTER_LEN + 1))

    assert shell._audit_filter == "Alice"
    assert shell._inv_filter == "Lipitor"
    assert shell.nav == ["admin", "admin"]
    assert errors and errors[-1][0] == "Audit Filter"


def test_admin_filter_summary_lists_active_filters():
    assert PharmacyApp._admin_filter_summary("", "") == ""
    assert PharmacyApp._admin_filter_summary("Alice", "") == "Audit: Alice"
    assert PharmacyApp._admin_filter_summary("", "Lipitor") == "Inventory: Lipitor"
    assert PharmacyApp._admin_filter_summary(
        "Alice", "Lipitor") == "Audit: Alice | Inventory: Lipitor"


def test_admin_clear_filters_resets_both_filters():
    shell = _shell()
    shell._audit_filter = "Alice"
    shell._inv_filter = "Lipitor"

    PharmacyApp._admin_clear_filters(shell)

    assert shell._audit_filter == ""
    assert shell._inv_filter == ""
    assert shell.nav == ["admin"]


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
