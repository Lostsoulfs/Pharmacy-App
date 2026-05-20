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
    """Ruff lint + format check."""
    session.install("ruff>=0.15")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


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
    """Layer 3: branch coverage with a term-missing report."""
    session.install("-r", "requirements-dev.txt")
    session.run(
        "pytest", f"--cov={PACKAGE}", "--cov-report=term-missing")


@nox.session
def seedsweep(session):
    """Advanced: sweep 50 random seeds, stop on the first failure."""
    session.install("-r", "requirements-dev.txt")
    for seed in range(1, 51):
        session.run("pytest", f"--randomly-seed={seed}", "-q")


@nox.session
def mutation(session):
    """Layer 4: mutation testing with mutmut (see KNOWN_ISSUES.md)."""
    session.install("-r", "requirements-dev.txt")
    session.run("mutmut", "run", success_codes=[0, 1, 2])
    session.run("mutmut", "results")
