#!/usr/bin/env python3
"""Display-free tests for PharmacyApp scroll event helpers."""

from types import SimpleNamespace

from pharmacy_app.app import PharmacyApp


class FakeCanvas:
    def __init__(self):
        self.calls = []

    def yview_scroll(self, amount, what):
        self.calls.append(("scroll", amount, what))

    def yview_moveto(self, fraction):
        self.calls.append(("moveto", fraction))


class FakeWidget:
    def __init__(self, widget_class):
        self.widget_class = widget_class

    def winfo_class(self):
        return self.widget_class


def _app_shell():
    return object.__new__(PharmacyApp)


def test_scroll_units_from_common_wheel_events():
    assert PharmacyApp._scroll_units_from_wheel_event(
        SimpleNamespace(delta=120)) == -1
    assert PharmacyApp._scroll_units_from_wheel_event(
        SimpleNamespace(delta=-240)) == 2
    assert PharmacyApp._scroll_units_from_wheel_event(
        SimpleNamespace(delta=1)) == -1
    assert PharmacyApp._scroll_units_from_wheel_event(
        SimpleNamespace(num=4)) == -1
    assert PharmacyApp._scroll_units_from_wheel_event(
        SimpleNamespace(num=5)) == 1
    assert PharmacyApp._scroll_units_from_wheel_event(SimpleNamespace()) == 0


def test_scroll_wheel_handler_scrolls_canvas_and_breaks_event():
    app = _app_shell()
    canvas = FakeCanvas()

    result = PharmacyApp._handle_scroll_wheel(
        app, canvas, SimpleNamespace(delta=-120))

    assert result == "break"
    assert canvas.calls == [("scroll", 1, "units")]


def test_scroll_key_handler_maps_navigation_keys():
    app = _app_shell()
    canvas = FakeCanvas()

    for key in ("Up", "Down", "Prior", "Next", "Home", "End"):
        assert PharmacyApp._handle_scroll_key(
            app, canvas, SimpleNamespace(keysym=key, widget=None)) == "break"

    assert canvas.calls == [
        ("scroll", -1, "units"),
        ("scroll", 1, "units"),
        ("scroll", -1, "pages"),
        ("scroll", 1, "pages"),
        ("moveto", 0.0),
        ("moveto", 1.0),
    ]


def test_scroll_key_handler_does_not_hijack_text_inputs():
    app = _app_shell()
    canvas = FakeCanvas()

    for widget_class in ("Entry", "Text", "Spinbox", "TEntry", "TCombobox"):
        event = SimpleNamespace(
            keysym="Down",
            widget=FakeWidget(widget_class),
        )
        assert PharmacyApp._handle_scroll_key(app, canvas, event) is None

    assert canvas.calls == []


def test_scroll_key_handler_ignores_unknown_keys():
    app = _app_shell()
    canvas = FakeCanvas()

    result = PharmacyApp._handle_scroll_key(
        app, canvas, SimpleNamespace(keysym="Left", widget=None))

    assert result is None
    assert canvas.calls == []
