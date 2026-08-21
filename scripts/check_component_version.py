#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
EXPECTED_REPOSITORY = "StegVerse-org/StegVerse-SDK"

def fail(msg: str) -> None:
    raise SystemExit(f"COMPONENT_VERSION=FAIL\n- {msg}")

if DATA.get("schema_version") != "1.0.0": fail("schema_version must be 1.0.0")
if DATA.get("repository") != EXPECTED_REPOSITORY: fail("repository identity mismatch")
if DATA.get("component_version") != "1.1.0": fail("canonical SDK component version must remain 1.1.0")
if DATA.get("version_stage") != "RELEASE_CANDIDATE": fail("SDK must remain RELEASE_CANDIDATE until exact publication evidence exists")
if DATA.get("authority_effect") != "NONE": fail("version declaration may not grant authority")
if DATA.get("credential_authority") != "TV/TVC" or DATA.get("release_authority") != "TV/TVC": fail("TV/TVC authority boundary drift")
if DATA.get("non_tv_tvc_release_credential_permitted") is not False: fail("non-TV/TVC release credential must remain prohibited")
release = DATA.get("release", {})
if release.get("tag") is not None or release.get("commit") is not None or release.get("release_evidence"):
    fail("release record must remain empty until actual publication is verified")
candidate = DATA.get("release_candidate", {})
if candidate.get("target_tag") != "v1.1.0": fail("target tag drift")
if candidate.get("frozen_commit") != "922d6c5235229e854c36e1a194dc99ed15a31b51": fail("frozen candidate drift")
if candidate.get("artifact_validation_state") != "PASS": fail("artifact validation must remain PASS")
if candidate.get("tag_publication") != "NOT_YET_AUTHORIZED": fail("tag publication state must remain not authorized")
if candidate.get("package_publication") != "NOT_YET_PUBLISHED": fail("package publication state must remain not published")
print("COMPONENT_VERSION=PASS")
print(f"COMPONENT_ID={DATA['component_id']}")
print(f"COMPONENT_VERSION_VALUE={DATA['component_version']}")
print("VERSION_STAGE=RELEASE_CANDIDATE")
print("AUTHORITY_EFFECT=NONE")
