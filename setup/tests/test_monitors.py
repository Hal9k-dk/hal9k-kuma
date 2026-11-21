"""Sanity checks for the declarative monitor definitions."""

from uptime_kuma_api import MonitorType

from main import HEARTBEAT_AGE_JSONPATH, MONITORS, RENAMES, push_url

PUSH_MONITORS = {m["name"]: m for m in MONITORS if m["type"] == MonitorType.PUSH}


def test_monitor_names_are_unique():
    names = [m["name"] for m in MONITORS]
    assert len(names) == len(set(names))


def test_renames_target_declared_monitors():
    names = {m["name"] for m in MONITORS}
    for old, new in RENAMES.items():
        assert new in names, f"rename target {new!r} is not a declared monitor"
        assert old not in names, f"rename source {old!r} is still declared"


def test_sofiendalsvej_push_monitors_exist():
    assert set(PUSH_MONITORS) == {
        "Sofiendalsvej IPv4 connectivity",
        "Sofiendalsvej IPv6 connectivity",
    }


def test_sofiendalsvej_monitors_use_tolerant_interval():
    for monitor in PUSH_MONITORS.values():
        assert monitor["interval"] == 300
        assert monitor["maxretries"] == 1


def test_push_url_strips_trailing_slash():
    assert push_url("https://status.example.dk/", "abc123") == "https://status.example.dk/api/push/abc123"
    assert push_url("https://status.example.dk", "abc123") == "https://status.example.dk/api/push/abc123"


def test_card_reader_monitors_tolerate_reboots():
    card_readers = [m for m in MONITORS if m.get("mqttTopic", "").startswith("hal9k/acs/status/") and m["name"].endswith("Card Reader")]
    assert len(card_readers) == 3
    for monitor in card_readers:
        # One beat after an ACS unit reboots, the reader reports the epoch as its
        # heartbeat; the JSONata guard maps that to "just seen".
        assert monitor["jsonPath"] == HEARTBEAT_AGE_JSONPATH
        assert "$hb = 0 ? 1" in monitor["jsonPath"]
        # ...and a single bad beat must not alert.
        assert monitor["maxretries"] == 1
