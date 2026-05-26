"""Debug logging utilities for pharmacy_app.

Usage:
    from pharmacy_app.debug_log import get_logger, trace, setup

    _log = get_logger(__name__)
    _log.debug("calc result: %s", value)

    @trace
    def my_fn(x):
        ...

Enable debug output: set PHARMACY_DEBUG=1 in the environment, then call
debug_log.setup() once at startup.  debug_run.py does this automatically
when --verbose is passed.
"""
import functools
import logging
import os


def setup(level=None):
    """Configure the pharmacy_app package logger.  Idempotent.

    level=None reads PHARMACY_DEBUG env var:
      PHARMACY_DEBUG=1  -> DEBUG
      anything else     -> WARNING
    """
    if level is None:
        level = logging.DEBUG if os.environ.get("PHARMACY_DEBUG") else logging.WARNING
    pkg = logging.getLogger("pharmacy_app")
    if not pkg.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "[%(levelname).1s %(name)s:%(lineno)d] %(message)s"
        ))
        pkg.addHandler(handler)
    pkg.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Return a logger under the pharmacy_app namespace."""
    return logging.getLogger(name)


def trace(fn):
    """Decorator: log function entry (args/kwargs) and return value at DEBUG.

    Example::

        from pharmacy_app.debug_log import trace

        @trace
        def calc_bsa_mosteller(height_cm, weight_kg):
            ...

    Only active when the calling module's logger is at DEBUG level;
    zero overhead in normal runs.
    """
    _log = logging.getLogger(fn.__module__)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if _log.isEnabledFor(logging.DEBUG):
            arg_str = ", ".join(
                [repr(a) for a in args]
                + [f"{k}={v!r}" for k, v in kwargs.items()]
            )
            _log.debug("→ %s(%s)", fn.__name__, arg_str)
        result = fn(*args, **kwargs)
        if _log.isEnabledFor(logging.DEBUG):
            _log.debug("← %s = %r", fn.__name__, result)
        return result

    return wrapper
