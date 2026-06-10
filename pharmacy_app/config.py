"""System constants and configuration.

No clinical data, no UI, no DB calls — just values. Safe to import
from anywhere.
"""

import os

MAX_LOG_ENTRIES = 10000  # A7 fix 2026-05-19: bumped from 500.
# Compliance use case: state board "show me 6 months of activity".
# Estimated load: 30-50 audit rows/day (logins, inventory, partials,
# exports, etc.) x ~180 days = ~7,200 rows. 10,000 covers 6mo with
# margin. DB cost: ~1 MB for 10k rows (timestamp+name+action). Phone
# storage trivial. Future ADR may revisit if multi-store / multi-
# pharmacist scaling enters scope.
LOCKOUT_THRESHOLD = 3
LOCKOUT_SECONDS = 300
RESERVED_TECH_NAMES = {'admin', 'global', 'system', 'pharmacist'}

# Fresh DB; legacy filename retired with the migration subsystem
# (ADR-C01). Path verified app-private on S23 Ultra / Pydroid 3
# (ADR-002): expanduser("~") -> /data/user/0/ru.iiec.pydroid3/app_HOME
DB_FILE = os.path.join(os.path.expanduser("~"), "pharmacy_master.db")

# Per-dataset verification (ADR-C05). Each value is the ISO date a
# pharmacist signed off the dataset, or False while it is still
# unverified. The UI shows a red UNVERIFIED banner for any dataset
# still False, and a dated confirmation once it is signed.
# Per ADR-C05 a dataset stays UNVERIFIED until a pharmacist confirms
# it — set a key to a date ONLY after the pharmacist signs the
# matching audit under docs/audits/. The 2026-05-20 automated audits
# are complete but await that sign-off, so all keys remain False.
DATA_VERIFIED = {
    "brand_generic":     False,
    "red_flags":         False,
    "lasa_pairs":        False,
    "sig_abbreviations": False,
    "common_rx_flags":   False,
    "vaccines":          False,
    "law":               False,
    "tpr":               False,
}


def is_unverified(domains):
    """True if the UNVERIFIED banner should show — i.e. any listed
    domain is not yet verified. Empty/unknown keys fail safe to
    unverified (banner shows)."""
    if not domains:
        return True
    return not all(DATA_VERIFIED.get(d) for d in domains)


def verified_on(domains):
    """The most recent verification date among `domains`, or None if
    any listed domain is still unverified."""
    if is_unverified(domains):
        return None
    return max(DATA_VERIFIED[d] for d in domains)
