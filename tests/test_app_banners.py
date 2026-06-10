#!/usr/bin/env python3
"""Static checks for the app.py UI layer.

app.py imports tkinter at module scope, so it cannot be imported in a
headless environment. These tests parse app.py as source (via ast,
which does not execute or import it) to validate the one piece of UI
wiring that fails silently: the domain keys passed to
_unverified_banner. A typo'd key there means a panel's UNVERIFIED
banner can never clear — invisible to any rendering test.

Run under pytest:   pytest tests/test_app_banners.py -q
Run standalone:     python tests/test_app_banners.py
"""

import ast
import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pharmacy_app.config import DATA_VERIFIED  # noqa: E402

APP_PY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pharmacy_app", "app.py")


def _banner_calls():
    with open(APP_PY, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    return [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "_unverified_banner"
    ]


def test_banner_call_sites_present():
    # 6 panels render a banner: quiz, law, tpr, vaccines, sig, lookup.
    assert len(_banner_calls()) >= 6


def test_banner_domain_keys_valid():
    for call in _banner_calls():
        assert len(call.args) >= 2, "_unverified_banner missing domains arg"
        domains = call.args[1]
        assert isinstance(domains, ast.List) and domains.elts, (
            "domains must be a non-empty list literal")
        for elt in domains.elts:
            assert isinstance(elt, ast.Constant), "domain key not a literal"
            assert isinstance(elt.value, str)
            assert elt.value in DATA_VERIFIED, (
                "unknown domain key %r — banner will never clear"
                % elt.value)


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
