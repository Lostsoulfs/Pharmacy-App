"""Task orchestration for the testing harness.

Wires the four playbook layers into named sessions so the whole suite
runs with one command.

    nox            # default set: lint, types, tests
    nox -l         # list every session
    nox -s tests   # run one session
    nox -s tests -- -k cockcroft   # args after -- go to pytest
"""
import nox

PACKAGE = "pharmacy_app"

# Sessions run on a bare `nox` invocation, fastest first.
nox.options.sessions = ["lint", "types", "tests"]


@nox.session
def lint(session):
    """Ruff pyflakes (`F`) check — matches the documented quality
    gate (CLAUDE.md): no new `F` errors. The repo carries known
    pre-existing E/W style debt that is deliberately not gated; run
    a full `ruff check .` by hand to review it."""
    session.install("ruff>=0.15")
    session.run("ruff", "check", "--select", "F", ".")


@nox.session
def types(session):
    """Static type checking with mypy."""
    session.install("mypy>=1.18")
    session.run("mypy", PACKAGE)


@nox.session
def tests(session):
    """Layers 1-2: example + property tests, run in parallel."""
    session.install("-r", "requirements-dev.txt")
    session.run("pytest", "-n", "auto", *session.posargs)


@nox.session
def coverage(session):
    """Layer 3: branch coverage with the configured baseline ratchet."""
    session.install("-r", "requirements-dev.txt")
    session.run(
        "pytest",
        f"--cov={PACKAGE}",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-report=html",
    )


@nox.session
def seedsweep(session):
    """Advanced: sweep 50 random seeds, stop on the first failure."""
    session.install("-r", "requirements-dev.txt")
    for seed in range(1, 51):
        session.run("pytest", f"--randomly-seed={seed}", "-q")


@nox.session
def contracts(session):
    """Symbolically check the clinical calculation rules with CrossHair."""
    session.install("-r", "requirements-dev.txt")
    session.run("crosshair", "check", "tools/crosshair_contracts.py")


@nox.session
def mutation(session):
    """Layer 4: mutation testing with mutmut (see KNOWN_ISSUES.md)."""
    session.install("-r", "requirements-dev.txt")
    session.run("mutmut", "run", success_codes=[0, 1, 2])
    session.run("mutmut", "results")
