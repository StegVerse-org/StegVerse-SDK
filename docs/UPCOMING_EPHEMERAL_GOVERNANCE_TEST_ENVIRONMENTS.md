# Upcoming test environments — portable ephemeral governance

Status: PROPOSED TEST ENVIRONMENTS / DOCUMENTATION ONLY / NOT A PRODUCT OR RELEASE COMMITMENT
Scope: Existing SDK and reusable StegVerse governance capabilities. This page does not introduce a new Task Registry goal, permanent runtime, Interlock/InTr authority, custody system, device dependency, or product announcement.

## Research objective

Test whether an independently operated framework can invoke a portable, purpose-bound StegVerse governance capability over a network, receive an authentic disposition and evidence package, and enable independent replay or reconstruction after the ephemeral execution environment has terminated. MIR is an intended independent historical-record participant and potential verifier, not a StegVerse execution or governance authority.

These are **upcoming environments for testing existing roadmap capabilities**, not named future products. Source conformance, proposed interfaces, authentic runtime observation, MIR retention, and third-party reconstruction must be reported as distinct evidence classes. An environment is not "available" simply because it is documented here.

## Existing SDK capability inventory and exact test gaps

This test plan reuses existing SDK implementation; it is **not** a request to develop replacement modules or a new product. Implemented code and source/CI evidence establish interface conformance, not authentic cross-system runtime completion.

| Existing SDK capability | Current implementation | What the proposed environments still need to demonstrate |
| --- | --- | --- |
| Generic manifested intake and selected processing | `stegverse/manifest_contract.py`, `stegverse/manifest_builder.py`, `stegverse/manifest_state_transition_runtime.py` and [generic processing contract](GENERIC_MANIFEST_PROCESSING_CONTRACT.md) | Actual authenticated Universal InTr admission and execution, not only source validation or a local diagnostic. |
| Participant Interlock and reciprocal return | Existing portable Interlock, standing/evidence bridge and reciprocal return contracts; see [minimal portable governance ecosystem](MINIMAL_PORTABLE_GOVERNANCE_ECOSYSTEM_MIRROR_HANDOFF.md) | Exact cross-network request identity, admitted decision, real bounded consequence and independent far-side return evidence. |
| Independent verifier | `stegverse/portable_governance_verifier.py`; stages `PRE_STEGGATE` and `POST_RETURN`; see [verifier handoff](PORTABLE_GOVERNANCE_VERIFIER_MIRROR_HANDOFF.md) | An authentic `POST_RETURN` production bundle tied to canonical StegGate decision/consequence and independently verified Master Records custody; a self-contained source fixture is insufficient. |
| Portable evidence exchange | `stegverse/portable_governance_exchange.py` and `stegverse-governance-exchange create/verify/extract`; see [exchange handoff](PORTABLE_GOVERNANCE_EVIDENCE_EXCHANGE_MIRROR_HANDOFF.md) | Archive actual original evidence; verify/extract it from a fresh external environment without treating the copied ZIP as canonical custody. |
| Exact-run replay and reconstruction | Existing SDK console options `1` and `2` using `manifest_receipt_id`; see [receipt navigation](MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md) | Independently retrieved original receipts, exact immediate-predecessor continuity and independently observed replay/reconstruction equality for the same authentic event. |
| MIR interface | MIR is an intended external record participant, not an existing SDK authority. | Implement or validate the scoped adapter for the **selected actual MIR interface**; authenticate publication and fresh retrieval; compare original immutable commitment and custody-backed evidence. No production MIR round trip is asserted. |

### Smallest integrative SDK test

Use one source-framework event and its exact immutable manifest. Submit it over the existing installed public SDK route; obtain actual native admission and bounded execution dispositions; retain exact organization and Master Records evidence; export that evidence using the already installed exchange; obtain MIR's own independently retrievable record/commitment; and let the originator or a third-party verifier fetch original custody evidence and rerun the existing verifier plus receipt-ID reconstruction. Retain the original source-framework observation separately from MIR's historical commitment and StegVerse's governance evidence.

The first failed actual boundary must produce its exact native disposition and repair ownership. A missing configured runtime or unreachable MIR service is **not** a passing end-to-end test, and absence of accessible receipts must not be interpreted as evidence no event happened. No extra resident, connected-device inventory or permanent network membership is a prerequisite.

## Candidate testing environments

| Environment | Boundary to exercise | Evidence needed |
| --- | --- | --- |
| Local/isolated SDK conformance | An external framework builds an original manifest and invokes the installed SDK validation/diagnostic route without claimed network authority. | Deterministic original bytes and hashes; typed source/profile dispositions; explicit NOT_OBSERVED for unavailable live evidence. No fabricated InTr ALLOW. |
| Authorized event-ephemeral runtime | Existing StegOS/Interlock/InTr path admits one original event with a bounded, current, request-bound lease; existing WorkerCoordinator claim/fence where applicable. | Actual admission/disposition, final native lease snapshot and expiry/revocation checks, execution or exact non-ALLOW, original predecessor-linked organization receipts and corresponding Master Records reconstruction. |
| Cross-network portable governance module | The same declared SDK contract executes from an eligible environment on a different network, communicating over authenticated existing Interlock/InTr routes, without relying on an always-connected user device, fixed machine or newly invented authority. | Request-bound identity and policy, transport/discovery evidence, current remote-authority checks, exact disposition, loss-of-network and revocation cases. Network presence never grants authority. |
| MIR historical commitment and retrieval | After an authentic governed event, an adapter submits the permitted record/commitment using MIR's applicable service and retrieves the same record independently. | Actual MIR response and immutable/append-only proof **only to the extent supported by the selected MIR interface**, stable record ID, exact digest comparison, separately retained original evidence. Do not equate participation-record retrieval with immutable full-evidence storage. |
| Originator or third-party reconstruction | The original submitting framework or another authorized verifier independently retrieves MIR's record and required canonical evidence and checks replay using the SDK verification format or independent implementation. | Original request equality, retained receipt/evidence hashes, immediate-predecessor order, reconstructed state comparison, disagreement/unknown classes, and mutation, omission and unavailable-evidence negative tests. |

## Portable invocation and evidence contract under test

1. **Submit:** An arbitrary participating framework supplies original manifested data, provenance, requested transition, purpose, declared observations, and required evidence/return profile through existing SDK manifest intake.
2. **Bind:** An existing authorized route determines current policy, caller identity, applicable delegated authority and TV/TVC credential requirements. The portable module neither mints governance authority nor inherits it merely by running on a network.
3. **Evaluate and execute:** Interlock/InTr issues the actual transition disposition. An ALLOW permits only its specified, still-current bounded consequence; every attempted transition produces a precise disposition. DENY routes actionable correction to existing owners where permitted. FAIL_CLOSED terminates the current attempt. A source/profile refusal must not be relabeled as an authentic InTr DENY.
4. **Retain:** Existing canonical custody preserves the exact decision, actual execution/failure state, required evidence and predecessor continuity. Master Records reconstruction gates the next state-dependent progression when applicable.
5. **Return and commit:** The SDK returns the evidence manifest and governed result. MIR may retain the agreed history/commitment through its own applicable interface. The SDK must not assume MIR retains the full original evidence bytes.
6. **Retrieve and verify:** A fresh verifier obtains the actual MIR record and corresponding authorized original evidence independently, recomputes all checks and reconstructs only what the observations support. Unobserved external/physical events remain unknown.
7. **Terminate:** The ephemeral execution authority expires or is revoked; the durable records and verification contract remain usable independently of that runtime. The original experiment's Publisher and far-side reviewer requirements remain separate completion conditions.

## Experiment 3 mapping, without redefining it

Existing `MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003` and its frozen source-scoped manifest provide an initial assessment fixture for **Observe, Demonstrate, Retain, Reconstruct**. Its frozen original bytes and existing Publisher-required review contract are unchanged. The actual network/MIR/third-party test samples are separately hash-bound successor runs; no successful local source test may be upgraded to evidence of MIR commitment, sovereign execution or independently verified reconstruction.

## Existing owners and reuse

- SDK generic manifest processing and downstream propagation remain under their registered SDK owners; do not duplicate intake or processors.
- Interlock/InTr, StegOS EVENT_EPHEMERAL, TV/TVC, WorkerCoordinator, canonical organization receipts, Master Records and SDK return/Publisher each retain existing authority and component ownership.
- Existing Experiment 3 source/lease repair PR #2742 and StegOS #127 are supporting implementation where their exact contracts apply, not a redefinition or global prerequisite for unrelated SDK tests.
- Existing public SDK wiki publication ownership and rules remain unchanged. This source document is not evidence of public deployment.

## Test reporting format

For **each** environment, report: exact fixture/event and source hashes; authority and network scope; what is specified; what actually executed; independently retrieved receipt IDs/proofs; reconstruction procedure and equality result; failures and explicit unknowns; independent reviewer disposition. Keep physical-world coverage distinct from cryptographic integrity and receipt completeness.

**Exit condition for this testing series:** At least one authentic cross-system event has completed the authorized ephemeral governance path, produced independently retrievable historical commitment and original evidence, and been reconstructed by a separately operated verifier, with negative cases correctly distinguished. This is a proposed test criterion, not a claim of current completion.
