#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/stegmerch/fictional/drop.valid.json"
def fail(message: str) -> None:
    raise SystemExit(f"STEGMERCH_VALIDATION_FAILED: {message}")
def main() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    required = {"schema_version","drop_id","design_ref","brand_authorization_ref","location_authorization_ref","opens_at","closes_at","currency","unit_price_minor","revenue_split","status"}
    missing = sorted(required - data.keys())
    if missing: fail(f"missing fields: {', '.join(missing)}")
    if not data["brand_authorization_ref"].startswith("brandauth_"): fail("brand authorization reference is absent or malformed")
    if not data["location_authorization_ref"].startswith("locauth_"): fail("location authorization reference is absent or malformed")
    if data["opens_at"] >= data["closes_at"]: fail("drop close must occur after open")
    if data["unit_price_minor"] <= 0: fail("unit price must be positive")
    split_total = sum(item.get("basis_points", -1) for item in data["revenue_split"])
    if split_total != 10000: fail(f"revenue split totals {split_total}, expected 10000")
    recipients = [item.get("recipient") for item in data["revenue_split"]]
    if len(recipients) != len(set(recipients)): fail("revenue split contains duplicate recipients")
    if data["status"] in {"ready", "open"}: fail("fictional fixture cannot authorize commerce activation")
    print("STEGMERCH_VALIDATION_PASSED")
if __name__ == "__main__": main()
