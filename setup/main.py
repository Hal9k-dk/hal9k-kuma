"""Configure Uptime Kuma monitors for drillpress services."""

import argparse
import logging
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from uptime_kuma_api import MonitorType, UptimeKumaApi

load_dotenv()

logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])
log = logging.getLogger(__name__)
console = Console()

# ---------------------------------------------------------------------------
# Service definitions — synced from live Kuma 2026-06-29
# ---------------------------------------------------------------------------

CONDITIONS_STALE_120S: list[dict] = [
    {"type": "expression", "variable": "json_value", "operator": "lt", "value": "120000", "andOr": "and"},
    {"type": "expression", "variable": "json_value", "operator": "gt", "value": "0", "andOr": "and"},
]

CONDITIONS_STALE_720S: list[dict] = [
    {"type": "expression", "variable": "json_value", "operator": "lt", "value": "720000", "andOr": "and"},
    {"type": "expression", "variable": "json_value", "operator": "gt", "value": "0", "andOr": "and"},
]

MONITORS: list[dict] = [
    # Public web services (HTTPS)
    {
        "name": "www.hal9k.dk",
        "type": MonitorType.HTTP,
        "url": "https://www.hal9k.dk",
        "maxretries": 0,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "name": "HAL9K WordPress",
        "type": MonitorType.HTTP,
        "url": "https://www.hal9k.dk",
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "name": "HAL9K WordPress (apex)",
        "type": MonitorType.HTTP,
        "url": "https://hal9k.dk",
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "name": "Panopticon ACS",
        "type": MonitorType.HTTP,
        "url": "https://panopticon.hal9k.dk",
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "name": "ACS Gateway",
        "type": MonitorType.JSON_QUERY,
        "url": "https://acsgateway.hal9k.dk/spaceapi",
        "jsonPath": "$.space",
        "expectedValue": "Hal9k",
        "jsonPathOperator": "==",
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "name": "DokuWiki",
        "type": MonitorType.HTTP,
        "url": "https://wiki.hal9k.dk",
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "name": "QR Redirect",
        "type": MonitorType.HTTP,
        "url": "https://qr.hal9k.dk",
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "name": "MinIO",
        "type": MonitorType.HTTP,
        "url": "https://minio.hal9k.dk/minio/health/live",
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "name": "Danske Domæneregistranter",
        "type": MonitorType.HTTP,
        "url": "https://registrant.dk/",
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
        # registrant.dk is IPv6-only; needs IPv6 reachability inside the Kuma container.
        "notificationIDList": [1],
    },
    # MQTT broker (TCP port check)
    {
        "name": "MQTT Broker",
        "type": MonitorType.PORT,
        "hostname": "mqtt.hal9k.dk",
        "port": 8883,
        "maxretries": 3,
    },
    # MeshCore presence checks (JSON_QUERY)
    {
        "name": "MeshCore hal9k_hq repeater",
        "type": MonitorType.JSON_QUERY,
        "url": "https://meshview.belunktum.dk/api/nodes/ced8d22404718cb716fe4356d80e06e0dbd06d9381d30c43578016db3dc37cf9",
        "jsonPath": "($millis() - $toMillis(node.last_heard))",
        "expectedValue": "86400000",
        "jsonPathOperator": "<",
        "maxretries": 0,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "name": "MeshCore hal9k_room",
        "type": MonitorType.JSON_QUERY,
        "url": "https://meshview.belunktum.dk/api/nodes/9e1ef540b5cfe1897b26220481b5af24027407a6faa7a31fd52d4efda7608242",
        "jsonPath": "($millis() - $toMillis(node.last_heard))",
        "expectedValue": "108000000",
        "jsonPathOperator": "<",
        "maxretries": 0,
        "accepted_statuscodes": ["200-299"],
    },
    # MQTT heartbeat monitors
    {
        "name": "MQTT Bridge",
        "type": MonitorType.MQTT,
        "hostname": "mqtt://mqtt.hal9k.dk",
        "port": 1883,
        "mqttTopic": "hal9k/bridge/heartbeat",
        "mqttCheckType": "json-query",
        "jsonPath": "($millis() - $toMillis(timestamp))",
        "jsonPathOperator": "==",
        "conditions": CONDITIONS_STALE_120S,
        "maxretries": 0,
    },
    {
        "name": "ACS Main",
        "type": MonitorType.PORT,
        "hostname": "mqtt.hal9k.dk",
        "port": 8883,
        "maxretries": 3,
    },
    {
        "name": "ACS Main Door Card Reader",
        "type": MonitorType.MQTT,
        "hostname": "mqtt://mqtt.hal9k.dk",
        "port": 1883,
        "mqttTopic": "hal9k/acs/status/main",
        "mqttCheckType": "json-query",
        "jsonPath": "($millis() - $toMillis(data.card_reader_heartbeat))",
        "jsonPathOperator": "==",
        "expectedValue": "true",
        "conditions": CONDITIONS_STALE_120S,
        "maxretries": 0,
    },
    {
        "name": "ACS Barn Door Card Reader",
        "type": MonitorType.MQTT,
        "hostname": "mqtt://mqtt.hal9k.dk",
        "port": 1883,
        "mqttTopic": "hal9k/acs/status/barndoor",
        "mqttCheckType": "json-query",
        "jsonPath": "($millis() - $toMillis(data.card_reader_heartbeat))",
        "jsonPathOperator": "==",
        "expectedValue": "true",
        "conditions": CONDITIONS_STALE_120S,
        "maxretries": 0,
    },
    {
        "name": "ACS Wood Shop Door Card Reader",
        "type": MonitorType.MQTT,
        "hostname": "mqtt://mqtt.hal9k.dk",
        "port": 1883,
        "mqttTopic": "hal9k/acs/status/woodshop",
        "mqttCheckType": "json-query",
        "jsonPath": "($millis() - $toMillis(data.card_reader_heartbeat))",
        "jsonPathOperator": "==",
        "expectedValue": "true",
        "conditions": CONDITIONS_STALE_120S,
        "maxretries": 0,
    },
    {
        "name": "ACS Sync ForeningLet",
        "type": MonitorType.MQTT,
        "hostname": "mqtt://mqtt.hal9k.dk",
        "port": 1883,
        "mqttTopic": "hal9k/acs/status/sync",
        "mqttCheckType": "json-query",
        "jsonPath": "($millis() - $toMillis(last_sync))",
        "jsonPathOperator": "==",
        "expectedValue": "true",
        "conditions": CONDITIONS_STALE_720S,
        "maxretries": 0,
    },
    # Push monitors reported by the onsite machine at Sofiendalsvej. The
    # machine sends a heartbeat to /api/push/<token> once per interval; a
    # missing heartbeat marks the corresponding address family as down.
    {
        "name": "Sofiendalsvej IPv4 connectivity",
        "type": MonitorType.PUSH,
        "interval": 300,
        "maxretries": 1,
    },
    {
        "name": "Sofiendalsvej IPv6 connectivity",
        "type": MonitorType.PUSH,
        "interval": 300,
        "maxretries": 1,
    },
]


def get_existing_monitors(api: UptimeKumaApi) -> dict[str, int]:
    """Return mapping of monitor name -> id for all existing monitors."""
    monitors = api.get_monitors()
    return {m["name"]: m["id"] for m in monitors}


def push_url(base_url: str, token: str) -> str:
    """Return the heartbeat URL a push monitor client should call."""
    return f"{base_url.rstrip('/')}/api/push/{token}"


def report_push_urls(api: UptimeKumaApi, ids: dict[str, int], base_url: str) -> None:
    """Print the heartbeat URL of every push monitor, for onsite setup.

    The token is read back per monitor instead of from the cached monitor
    list, which does not yet contain monitors created in this run.
    """
    push_monitors = [mon["name"] for mon in MONITORS if mon["type"] == MonitorType.PUSH]
    if not push_monitors:
        return
    console.print(f"[bold]Push heartbeat URLs ({base_url}):[/bold]")
    for name in push_monitors:
        if name not in ids:
            console.print(f"  {name}: [yellow]pending[/yellow] (created on first apply)")
            continue
        token = api.get_monitor(ids[name])["pushToken"]
        console.print(f"  {name}: {push_url(base_url, token)}")


def apply_monitors(api: UptimeKumaApi, base_url: str, dry_run: bool = False) -> None:
    existing = get_existing_monitors(api)
    ids = dict(existing)
    console.print(f"[bold]Found {len(existing)} existing monitor(s)[/bold]")

    # ACS Tester was an obsolete duplicate of the MQTT Bridge monitor.
    if "ACS Tester" in existing:
        log.info("Deleting obsolete monitor: ACS Tester")
        if not dry_run:
            api.delete_monitor(existing["ACS Tester"])
            log.info("  Deleted: ACS Tester")
        else:
            console.print("  [yellow][dry-run][/yellow] Would delete: ACS Tester")

    for mon in MONITORS:
        name = mon["name"]
        if name in existing:
            log.info("Updating monitor: %s", name)
            if not dry_run:
                api.edit_monitor(existing[name], **mon)
                log.info("  Updated: %s", name)
            else:
                console.print(f"  [yellow][dry-run][/yellow] Would update: {name}")
        else:
            log.info("Creating monitor: %s", name)
            if not dry_run:
                response = api.add_monitor(**mon)
                ids[name] = response["monitorID"]
                log.info("  Created: %s", name)
            else:
                console.print(f"  [yellow][dry-run][/yellow] Would create: {name}")

    report_push_urls(api, ids, base_url)
    console.print("[green]Done.[/green]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Configure Uptime Kuma monitors for drillpress")
    parser.add_argument("--url", default=os.environ.get("KUMA_URL", "http://localhost:3001"), help="Uptime Kuma base URL")
    parser.add_argument("--username", default=os.environ.get("KUMA_USER", "admin"), help="Uptime Kuma username")
    parser.add_argument("--password", default=os.environ.get("KUMA_PASSWORD"), help="Uptime Kuma password")
    parser.add_argument(
        "--public-url",
        default=os.environ.get("KUMA_PUBLIC_URL"),
        help="Externally reachable Kuma base URL, used when printing push heartbeat URLs (defaults to --url)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without making changes")
    args = parser.parse_args()

    if not args.password:
        parser.error("Password required: set --password or KUMA_PASSWORD env var")

    public_url = args.public_url or args.url

    console.print(f"Connecting to Uptime Kuma at [bold]{args.url}[/bold] …")
    with UptimeKumaApi(args.url, timeout=30) as api:
        api.login(args.username, args.password)
        console.print("[green]Logged in.[/green]")
        apply_monitors(api, public_url, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
