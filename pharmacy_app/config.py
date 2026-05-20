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

# Per-dataset verification (replaces the ADR-C05 global flag). Each
# value is the ISO date the dataset was verified, or False if it is
# still unverified. The UI shows a red UNVERIFIED banner for any
# dataset still False, and a dated confirmation for verified ones.
# Setting a key to a date is a clinical assertion — only do it after
# a documented audit under docs/audits/.
DATA_VERIFIED = {
    "brand_generic":     "2026-05-20",
    "red_flags":         "2026-05-20",
    "lasa_pairs":        "2026-05-20",
    "sig_abbreviations": "2026-05-20",
    "common_rx_flags":   "2026-05-20",
    "vaccines":          "2026-05-20",
    "law":               "2026-05-20",
    "tpr":               "2026-05-20",
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
