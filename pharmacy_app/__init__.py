"""Pharmacy Training & Workflow OS — modular package.

Refactored from the single-file pharmacy_rebuild.py (2,635 LOC) into a
package. Behavior-preserving: code is relocated, not rewritten.

Module layout:
- config        system constants / paths
- theme         colors and fonts
- clinical_data UNVERIFIED v13 clinical/law reference data (ADR-C05)
- logic         pure logic core, headlessly testable, no tkinter/sqlite
- data          SQLite data layer (fresh DB, parameterized writes)
- app           Tkinter UI (PharmacyApp)

Entrypoint: main.py at the repo root.
"""

__version__ = "0.2.0-modular"
