#!/usr/bin/env python3
"""Pharmacy Training & Workflow OS — entrypoint.

Pydroid 3: open this file and press Play.
Desktop: `python main.py` from the repo root.

The modular package lives in pharmacy_app/. This launcher wires the
data layer (DB init) to the UI layer (PharmacyApp) and starts the
Tk main loop.
"""

import tkinter as tk

from pharmacy_app.data import init_db
from pharmacy_app.app import PharmacyApp


def main():
    init_db()
    root = tk.Tk()
    PharmacyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
