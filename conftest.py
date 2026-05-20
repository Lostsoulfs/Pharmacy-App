"""Shared pytest config — Hypothesis profiles + reproducible seeds.

Works alongside pytest-randomly (from requirements-dev.txt), which
randomizes test order and prints a reproducible seed on every run.
"""
import os

from hypothesis import HealthCheck, settings

# --- Hypothesis profiles --------------------------------------------
# dev       : fast, for local iteration (default)
# ci        : thorough, for the pipeline
# crosshair : symbolic backend — proves properties instead of sampling
#             them. Registered only when hypothesis-crosshair is
#             installed (it's in requirements-dev.txt).
#
# Select with the HYPOTHESIS_PROFILE env var, e.g.:
#   HYPOTHESIS_PROFILE=ci pytest
settings.register_profile("dev", max_examples=50)
settings.register_profile(
    "ci", max_examples=500, deadline=None,
    suppress_health_check=[HealthCheck.too_slow])

try:
    import hypothesis_crosshair  # noqa: F401
    settings.register_profile(
        "crosshair", max_examples=20, deadline=None, backend="crosshair")
except ImportError:
    pass

settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))

# --- Multi-seed reproducibility -------------------------------------
# pytest-randomly resets the seed each run and prints it, e.g.:
#     Using --randomly-seed=123456789
#
# Reproduce a specific failure:
#     pytest -p randomly --randomly-seed=123456789
#
# Sweep many seeds (a green single run only proves "passed for one
# seed", not "passed"):
#     for s in $(seq 1 50); do pytest --randomly-seed=$s -q || break; done
