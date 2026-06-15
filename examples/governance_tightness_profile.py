from __future__ import annotations

import json

from stegverse.governance_tightness import apply_tightness_to_ingestion_packet, resolve_tightness_dict


def main() -> None:
    packet = {
        "schema": "stegverse.ingestion.cross_repo_task.v1",
        "source_org": "StegVerse-org",
        "source_repo": "StegVerse-SDK",
        "target_org": "StegVerse-Labs",
        "target_repo": "Site",
        "task": "publish governed admissibility exchange support",
    }

    output = {
        "observe": resolve_tightness_dict("observe"),
        "balanced": resolve_tightness_dict("balanced"),
        "strict": resolve_tightness_dict("strict"),
        "packet_with_tightness": apply_tightness_to_ingestion_packet(packet, {"scale": 55}),
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
