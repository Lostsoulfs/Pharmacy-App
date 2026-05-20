# Testing Playbook

The harness layers four techniques. Each catches what the previous
misses. Add them in order — don't skip ahead.

> Orchestration: `noxfile.py` wraps every layer below into named
> sessions — `nox` runs lint + types + tests, `nox -s coverage`,
> `nox -s seedsweep`, `nox -s mutation`. Run tools directly while
> iterating; use nox for the full sweep and in CI.

## 1. Example tests
Fixed inputs, readable, document *intent*. The baseline: fast to
write, fast to run. Weak spot — they only test the cases you thought
of.

Once the suite grows, run it in parallel: `pytest -n auto`
(pytest-xdist) spreads tests across every core.

## 2. Property-based tests (Hypothesis)
State an *invariant* ("output is always sorted", "ease never drops
below 1.3") and let Hypothesis generate inputs trying to break it.
Catches the cases you didn't think of, and shrinks any failure to a
minimal example.

Feed it junk deliberately: `None`, `NaN`, empty, huge, wrong types.
Scope strategies to the *real* input domain — testing values that the
system can never actually produce just invents fake bugs.

## 3. Branch coverage (pytest-cov)
    pytest --cov=pharmacy_app --cov-report=term-missing

Coverage tells you what code *ran*, not whether it was *checked*. 100%
coverage with weak assertions is worthless. Treat coverage as a floor
to clear, never a goal to optimize.

## 4. Mutation testing (mutmut)
The real test of your tests. mutmut changes your code (`+`->`-`,
`>`->`>=`, `True`->`False`, ...) and reruns the suite. A *surviving*
mutant is a change no test noticed — a genuine gap. Kill it with a
Layer-3 test. (See KNOWN_ISSUES.md for the mutmut 3.5.0 bug.)

## Advanced vectors

### Multi-seed sweeps
One green run means "passed for one seed", not "passed". Sweep:

    for s in $(seq 1 50); do pytest --randomly-seed=$s -q || break; done

`nox -s seedsweep` does the same. Run it as a nightly CI job; fail on
the first bad seed and report it so the failure is reproducible.

### Symbolic execution (CrossHair)
    HYPOTHESIS_PROFILE=crosshair pytest

Runs property tests through an SMT solver: it *proves* the invariant
holds, or returns an exact counterexample — instead of sampling.
Slower; run as a separate, non-blocking job. Best on pure, annotated
functions.

### Deterministic clock
If code reads `datetime.now()`, its tests are time-dependent and can
pass or fail by accident. Freeze the clock (freezegun, or inject a
`now` parameter) so behavior is tested at controlled instants.

## Order of effort
Examples and properties first — they find bugs. Coverage and mutation
second — they find gaps in the tests. The advanced vectors are for
code that genuinely warrants it (pure logic cores, anything where a
silent wrong answer is costly).
