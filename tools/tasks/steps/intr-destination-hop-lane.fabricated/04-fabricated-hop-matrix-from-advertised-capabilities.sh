set -eu
python -m unittest tests.test_intr_destination_hop_lane.FabricatedCheckoutTests -v
args=()
for root in _orgs/SV-011 _orgs/GCAT-BCAT-Engine _orgs/StegVerse-002 _orgs/StegGhost; do
  if [ -d "$root" ]; then
    args+=(--org-root "$root")
  fi
done
python -m stegverse.intr_destination_hop_lane \
  --mode fabricated \
  --reference-root "$GITHUB_WORKSPACE/_orgs/StegVerse-org" \
  --org-root "$GITHUB_WORKSPACE/_orgs/StegVerse-org" \
  --org-root "$GITHUB_WORKSPACE/_orgs/StegVerse-Labs" \
  --org-root "$GITHUB_WORKSPACE/_orgs/SV-LLM" \
  --org-root "$GITHUB_WORKSPACE/_orgs/Admissible-Existence" \
  "${args[@]}" \
  --mesh-root "$RUNNER_TEMP/intr-hop-mesh" \
  --ledger-home "$RUNNER_TEMP/intr-hop-ledgers" \
  --out-dir "$RUNNER_TEMP/intr-hop-lane"
python - <<'PY'
import json, os
report = json.load(open(os.environ["RUNNER_TEMP"] + "/intr-hop-lane/intr-destination-hop-lane.json", encoding="utf-8"))
assert report["evidence_class"] == "FABRICATED_NON_AUTHENTIC", report["evidence_class"]
assert report["far_side_authentic"] is False
assert report["authenticity_claimed"] is False
assert report["federation_json_is_a_peer_source"] is False
assert report["counts"]["FAIL"] == 0, report["counts"]
assert report["counts"]["PASS"] == report["hop_count"] > 0
print("INTR_DESTINATION_HOP_LANE_FABRICATED_PASS hops=%d" % report["hop_count"])
PY
