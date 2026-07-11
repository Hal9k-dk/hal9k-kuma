"""Fetch current monitors from Uptime Kuma and print them as a MONITORS list."""

import os

from dotenv import load_dotenv
from uptime_kuma_api import MonitorType, UptimeKumaApi

load_dotenv()

KUMA_URL = os.environ.get("KUMA_URL", "http://localhost:3001")
KUMA_USER = os.environ.get("KUMA_USER", "admin")
KUMA_PASSWORD = os.environ.get("KUMA_PASSWORD", "")


def main() -> None:
    if not KUMA_PASSWORD:
        print("Error: KUMA_PASSWORD not set")
        return

    print(f"Connecting to {KUMA_URL} …")
    with UptimeKumaApi(KUMA_URL, timeout=30) as api:
        api.login(KUMA_USER, KUMA_PASSWORD)
        monitors = api.get_monitors()

    print(f"Found {len(monitors)} monitor(s):\n")
    print("MONITORS: list[dict] = [")

    for m in monitors:
        mtype = MonitorType(m["type"])
        name = m["name"]
        fields: dict[str, str | int | list[str]] = {"name": name, "type": mtype}

        match mtype:
            case MonitorType.HTTP:
                fields["url"] = m.get("url", "")
                fields["maxretries"] = m.get("maxretries", 0)
                if accepted := m.get("accepted_statuscodes"):
                    fields["accepted_statuscodes"] = accepted
            case MonitorType.MQTT:
                fields["hostname"] = m.get("hostname", "")
                fields["port"] = m.get("port", 0)
                fields["mqttTopic"] = m.get("mqttTopic", "")
                fields["maxretries"] = m.get("maxretries", 0)
                if check_type := m.get("mqttCheckType"):
                    fields["mqttCheckType"] = check_type
                if json_path := m.get("jsonPath"):
                    fields["jsonPath"] = json_path
                if json_op := m.get("jsonPathOperator"):
                    fields["jsonPathOperator"] = json_op
            case MonitorType.JSON_QUERY:
                fields["url"] = m.get("url", "")
                fields["jsonPath"] = m.get("jsonPath", "")
                fields["expectedValue"] = m.get("expectedValue", "")
                fields["maxretries"] = m.get("maxretries", 0)
                if accepted := m.get("accepted_statuscodes"):
                    fields["accepted_statuscodes"] = accepted
                if json_op := m.get("jsonPathOperator"):
                    fields["jsonPathOperator"] = json_op
            case MonitorType.PORT:
                fields["hostname"] = m.get("hostname", "")
                fields["port"] = m.get("port", 0)
                fields["maxretries"] = m.get("maxretries", 0)
            case MonitorType.PING:
                fields["hostname"] = m.get("hostname", "")
                fields["maxretries"] = m.get("maxretries", 0)
            case MonitorType.DNS:
                fields["hostname"] = m.get("hostname", "")
                fields["maxretries"] = m.get("maxretries", 0)
            case MonitorType.KEYWORD:
                fields["url"] = m.get("url", "")
                fields["keyword"] = m.get("keyword", "")
                fields["maxretries"] = m.get("maxretries", 0)
            case MonitorType.GROUP:
                pass
            case _:
                fields["_raw"] = str(m)

        lines = [f'        "{k}": {v!r},' for k, v in fields.items()]
        print("    {")
        for line in lines:
            print(f"    {line}")
        print("    },")

    print("]")

    # Also print IDs for reference
    print("\n# Name → ID mapping:")
    for m in monitors:
        print(f"#   {m['name']!r}: {m['id']}")


if __name__ == "__main__":
    main()
