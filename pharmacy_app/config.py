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

# UNVERIFIED clinical/law data carried as-is per ADR-C05; the UI layer
# MUST render this flag visibly next to any clinical/law entry.
CLINICAL_DATA_UNVERIFIED = True
