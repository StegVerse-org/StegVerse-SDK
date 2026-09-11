#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
EXPECTED_REPOSITORY = "StegVerse-org/StegVerse-SDK"
EXPECTED_VERSION = "1.3.0"
EXPECTED_TAG = "v1.3.0"
EXPECTED_SOURCE_PARENT = "b229a7a93a59bdd93e134ed1e219e482a81aefb1"
PRIOR_FROZEN_VERSION = "1.2.0"
PRIOR_FROZEN_TAG = "v1.2.0"
PRIOR_FROZEN_COMMIT = "beaabe0a06ef32f0f62fbe6bc360463b245bff61"


def fail(msg: str) -> None:
    raise SystemExit(f"COMPONENT_VERSION=FAIL\n- {msg}")


if DATA.get("schema_version") != "1.0.0":
    fail("schema_version must be 1.0.0")
if DATA.get("repository") != EXPECTED_REPOSITORY:
    fail("repository identity mismatch")
if DATA.get("component_version") != EXPECTED_VERSION:
    fail(f"SDK source-candidate version must be {EXPECTED_VERSION}")
if DATA.get("version_stage") != "SOURCE_CANDIDATE":
    fail("SDK 1.3.0 must remain SOURCE_CANDIDATE until exact freeze validation exists")
if DATA.get("authority_effect") != "NONE":
    fail("version declaration may not grant authority")
if DATA.get("credential_authority") != "TV/TVC" or DATA.get("release_authority") != "TV/TVC":
    fail("TV/TVC authority boundary drift")
if DATA.get("non_tv_tvc_release_credential_permitted") is not False:
    fail("non-TV/TVC release credential must remain prohibited")

release = DATA.get("release", {})
if release.get("tag") is not None or release.get("commit") is not None or release.get("release_evidence"):
    fail("release record must remain empty until actual publication is verified")

candidate = DATA.get("release_candidate", {})
if candidate.get("target_tag") != EXPECTED_TAG:
    fail("target tag drift")
if candidate.get("source_parent") != EXPECTED_SOURCE_PARENT:
    fail("source parent drift")
if candidate.get("candidate_branch") != "sdk-1.3.0-successor-candidate":
    fail("candidate branch drift")
if candidate.get("frozen_commit") is not None:
    fail("source candidate must not claim an exact frozen commit before freeze validation")
if candidate.get("artifact_validation_run") is not None:
    fail("source candidate must not predeclare artifact validation evidence")
if candidate.get("artifact_validation_state") != "PENDING":
    fail("source candidate artifact validation must remain PENDING until observed")
if candidate.get("tag_publication") != "NOT_YET_AUTHORIZED":
    fail("tag publication state must remain not authorized")
if candidate.get("package_publication") != "NOT_YET_PUBLISHED":
    fail("package publication state must remain not published")

prior = DATA.get("prior_frozen_release_identity", {})
if prior.get("version") != PRIOR_FROZEN_VERSION:
    fail("prior frozen release version drift")
if prior.get("tag") != PRIOR_FROZEN_TAG:
    fail("prior frozen release tag drift")
if prior.get("release_commit") != PRIOR_FROZEN_COMMIT:
    fail("prior frozen release commit drift")
if prior.get("retargeting_permitted") is not False:
    fail("prior frozen release must remain immutable")

print("COMPONENT_VERSION=PASS")
print(f"COMPONENT_ID={DATA['component_id']}")
print(f"COMPONENT_VERSION_VALUE={DATA['component_version']}")
print("VERSION_STAGE=SOURCE_CANDIDATE")
print(f"TARGET_TAG={EXPECTED_TAG}")
print(f"SOURCE_PARENT={EXPECTED_SOURCE_PARENT}")
print("PRIOR_V1_2_0_RETARGETING_PERMITTED=false")
print("AUTHORITY_EFFECT=NONE")
