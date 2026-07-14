# StegMerch Mirror Handoff

## Source of truth

This file is the current incubation handoff and task source of truth for the proposed StegMerch capability within `StegVerse-org/StegVerse-SDK`.

StegMerch is not yet a released product, approved storefront, authorized Fit4Mom program, or independent repository. This record preserves the concept, boundaries, blockers, and permitted continuation scope until a dedicated destination is approved.

## Current goal

```text
Goal: validate a repeatable, governed micro-commerce system for independently operated community organizations
Initial market hypothesis: independently owned and operated Fit4Mom franchise locations
Initial product: location-specific print-on-demand apparel
Validation mode: non-inventory pilot specification only
Revenue target hypothesis: $100,000+ recurring annual platform contribution
Current state: INCUBATION_HANDOFF_CREATED
Brand authorization: NOT VERIFIED
Commerce activation: NOT AUTHORIZED
Public sales: NOT AUTHORIZED BY THIS HANDOFF
```

## Initial product definition

### Front placement

Horizontally centered just below the collar:

```text
Fit4Mom
{Location}
```

### Reverse placement

Horizontally centered just below the collar:

```text
Hanging with my
BMFs!
```

The exact capitalization, trademark presentation, approved fonts, colors, garment placement, and wording remain subject to written brand and franchise authorization.

## Business-system model

StegMerch is the infrastructure layer. The community merch network is the recurring economic layer built on top of it.

```text
StegMerch infrastructure
  -> governed design templates
  -> location-variable generation
  -> storefront or checkout provisioning
  -> product and drop declarations
  -> fulfillment-provider routing
  -> revenue-split declarations
  -> order, fulfillment, refund, and payout receipts
  -> custody and reconstruction pointers

Community network
  -> independently operated location nodes
  -> recurring limited-duration drops
  -> shared campaign calendar
  -> local leader participation
  -> expansion to other identity-based communities after pilot validation
```

## Revenue hypothesis

The current threshold model is:

```text
300 communities
x 2 drops per year
x 40 units per drop
x $5 net platform contribution per unit
= $120,000 annual platform contribution
```

This is a planning hypothesis, not a forecast. Provider costs, taxes, refunds, chargebacks, shipping, licensing, customer acquisition, payment fees, franchise compensation, and brand royalties must be included before any profitability claim.

## Pilot phases

### Phase 0 — authorization and economics

1. Obtain written permission to use Fit4Mom names, marks, franchise-location identifiers, and proposed wording.
2. Determine whether authorization must come from the franchisor, each franchisee, or both.
3. Verify whether `BMFs` and the proposed phrase are acceptable for branded merchandise.
4. Select a print-on-demand and commerce provider only after current cost, payout, tax, return, API, and white-label terms are compared.
5. Define the lawful merchant of record and seller-of-record structure.

### Phase 1 — single-location demand test

1. One authorized location.
2. One approved design.
3. One limited-duration preorder or print-on-demand drop.
4. No inventory commitment unless preorder volume justifies a bulk print run.
5. Capture conversion, refund, fulfillment, margin, and satisfaction evidence.

### Phase 2 — ten-location repeatability test

1. Parameterized `{Location}` template.
2. Location authorization record per node.
3. Repeatable storefront and fulfillment configuration.
4. Explicit revenue-split agreement.
5. Standard campaign and closeout receipts.

### Phase 3 — governed network

1. Signed design declaration.
2. Brand-policy and location-authorization references.
3. Product, price, tax, fulfillment, and payout manifests.
4. Order-state event receipts.
5. Refund and dispute records.
6. Master-record custody pointers.
7. Reconstructable drop closeout packet.

### Phase 4 — cross-community expansion

Expansion beyond Fit4Mom is permitted only after the pilot proves authorization, positive contribution margin, repeatable operations, customer satisfaction, and reconstructable accounting.

## Required governed objects

```text
design_manifest
brand_authorization_record
location_authorization_record
product_manifest
drop_manifest
pricing_manifest
revenue_split_manifest
fulfillment_provider_manifest
order_event_receipt
fulfillment_event_receipt
refund_event_receipt
payout_event_receipt
drop_closeout_report
custody_pointer
reconstruction_manifest
```

Each object must distinguish declaration, authorization, execution, observation, custody, and reconstruction. A design declaration does not grant trademark permission. A provider connection does not authorize sales. A payment event does not prove final distributable profit.

## Authority boundary

```text
Idea != brand authorization.
Template != approved merchandise.
Franchise interest != franchisor permission.
Storefront creation != commerce activation authority.
Order receipt != fulfilled order.
Gross margin != net profit.
Provider payout != complete revenue distribution.
SDK capability != merchant-of-record authority.
Pilot evidence != permission to scale.
This handoff does not authorize public use of Fit4Mom trademarks.
```

## Known blockers

1. Written brand and trademark authorization has not been verified.
2. Fit4Mom franchise agreement restrictions have not been reviewed.
3. The merchant of record has not been selected.
4. Current print-on-demand costs and API terms have not been verified.
5. Tax, returns, refunds, chargebacks, and customer-service ownership are undefined.
6. Revenue split and franchise compensation agreements are undefined.
7. A dedicated StegMerch repository does not yet exist or has not been identified.
8. Master-Records custody and reconstruction integration is not specified.
9. Site presentation and checkout integration are not authorized.

## Destination candidates

```text
Temporary incubation: StegVerse-org/StegVerse-SDK
Preferred implementation destination: new dedicated StegMerch repository after approval
Potential public presentation: StegVerse-Labs/Site only after Site handoff permits the integration
Potential custody: master-records ecosystem destination selected by orchestration
Potential publication synchronization after release readiness:
  - StegVerse-Labs/Site
  - GCAT-BCAT-Engine/Publisher
  - admissibility-wiki
  - stegguardian-wiki
```

## Permitted continuation scope

The current authorized work is limited to:

1. Preserve requirements and decisions.
2. Define schemas and interfaces without activating commerce.
3. Compare current providers and economics.
4. Draft authorization and pilot requirements.
5. Create test fixtures using fictional brands and locations.
6. Propose the dedicated repository boundary.
7. Prepare a non-production SDK interface.

The following are not authorized by this handoff:

1. Publishing or selling Fit4Mom-branded products.
2. Claiming affiliation, endorsement, licensing, or approval.
3. Creating live checkout routes.
4. Collecting customer payments.
5. Configuring production secrets.
6. Tagging or releasing StegMerch as production-ready.

## Next task

```text
1. Create the implementation issue that owns the incubation work.
2. Add schema drafts for design, authorization, drop, pricing, order-event, payout, and closeout objects.
3. Add fictional-brand fixtures and validation tests.
4. Produce a current provider economics comparison.
5. Define repository-creation criteria and destination ownership.
6. Seek written brand/franchise authorization before any Fit4Mom-facing pilot.
7. Do not alter StegVerse-Labs/Site until docs/SITE_MIRROR_HANDOFF.md explicitly permits this integration.
```

## Completion criteria for incubation

Incubation reaches 100% only when:

1. The governed object schemas and validators exist.
2. Fictional fixtures pass validation.
3. Current provider economics are documented.
4. Merchant-of-record and legal responsibility options are documented.
5. Repository destination is approved.
6. A successor handoff is committed in the destination repository.
7. Ownership and permitted activation scope are explicit.

## Archive readiness

This handoff preserves the session decisions, product hypothesis, revenue model, blockers, authority boundaries, remaining work, and permitted continuation scope. The originating conversation is no longer required once the companion implementation issue is created and verified.
