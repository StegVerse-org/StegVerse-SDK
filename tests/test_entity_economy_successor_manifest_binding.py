import hashlib
from scripts.build_entity_economy_successor_manifests import ARTIFACTS,SOURCE_COMMIT,build
V1="""# The StegVerse Entity Economy — Volume I — 2026-09-29 Convergence Successor\n\n**Edition ID:** `stegverse-entity-economy-volume-i-2026-09-29-convergence`  \n**Lifecycle:** MATERIALIZED_SOURCE_NOT_PUBLISHED  \n**Historical predecessor SHA-256:** `a831891cee4c4e7a920ed6d38090672e0722b434a5941632620c3e11d8e4da95`  \n**Historical predecessor mutation:** PROHIBITED\n""".encode("utf-8")
def test_canonical_bindings_are_source_only():
 assert SOURCE_COMMIT=="1b4b7b1defd46fe5c537ef67fe4a12085143f777"
 assert set(ARTIFACTS)=={"I","II"} and ARTIFACTS["I"]["path"]!=ARTIFACTS["II"]["path"] and ARTIFACTS["I"]["sha256"]!=ARTIFACTS["II"]["sha256"]
 for a in ARTIFACTS.values(): assert len(a["sha256"])==64 and len(a["blob"])==40 and a["path"].startswith("papers/")
def test_tampered_source_rejected_before_manifest():
 try: build("I",V1)
 except ValueError as e: assert str(e)=="canonical_successor_sha256_mismatch"
 else: raise AssertionError("tampered/incomplete source accepted")
