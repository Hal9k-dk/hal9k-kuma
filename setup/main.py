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
    {"type": "expression", "variable": "json_value", "operator": "lt", "value": "120", "andOr": "and"},
]

CONDITIONS_STALE_720S: list[dict] = [
    {"type": "expression", "variable": "json_value", "operator": "lt", "value": "720", "andOr": "and"},
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
        "jsonPath": '($millis() - $toMillis(node.last_heard)) / (1000 * 60 * 60)',
        "expectedValue": "24",
        "jsonPathOperator": "<",
        "maxretries": 0,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "name": "MeshCore hal9k_room",
        "type": MonitorType.JSON_QUERY,
        "url": "https://meshview.belunktum.dk/api/nodes/9e1ef540b5cfe1897b26220481b5af24027407a6faa7a31fd52d4efda7608242",
        "jsonPath": '($millis() - $toMillis(node.last_heard)) / (1000 * 60 * 60)',
        "expectedValue": "30",
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
        "jsonPath": "($millis() - $toMillis(timestamp)) / 1000",
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
        "jsonPath": '($millis() - $toMillis(data.card_reader_heartbeat + "Z")) / 1000',
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
        "jsonPath": '($millis() - $toMillis(data.card_reader_heartbeat + "Z")) / 1000',
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
        "jsonPath": '($millis() - $toMillis(data.card_reader_heartbeat + "Z")) / 1000',
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
        "jsonPath": "($millis() - $toMillis(last_sync + \"Z\")) / 1000",
        "jsonPathOperator": "==",
        "expectedValue": "true",
        "conditions": CONDITIONS_STALE_720S,
        "maxretries": 0,
    },
]


def get_existing_monitors(api: UptimeKumaApi) -> dict[str, int]:
    """Return mapping of monitor name -> id for all existing monitors."""
    monitors = api.get_monitors()
    return {m["name"]: m["id"] for m in monitors}


def apply_monitors(api: UptimeKumaApi, dry_run: bool = False) -> None:
    existing = get_existing_monitors(api)
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
                api.add_monitor(**mon)
                log.info("  Created: %s", name)
            else:
                console.print(f"  [yellow][dry-run][/yellow] Would create: {name}")

    console.print("[green]Done.[/green]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Configure Uptime Kuma monitors for drillpress")
    parser.add_argument("--url", default=os.environ.get("KUMA_URL", "http://localhost:3001"), help="Uptime Kuma base URL")
    parser.add_argument("--username", default=os.environ.get("KUMA_USER", "admin"), help="Uptime Kuma username")
    parser.add_argument("--password", default=os.environ.get("KUMA_PASSWORD"), help="Uptime Kuma password")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without making changes")
    args = parser.parse_args()

    if not args.password:
        parser.error("Password required: set --password or KUMA_PASSWORD env var")

    console.print(f"Connecting to Uptime Kuma at [bold]{args.url}[/bold] …")
    with UptimeKumaApi(args.url, timeout=30) as api:
        api.login(args.username, args.password)
        console.print("[green]Logged in.[/green]")
        apply_monitors(api, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
