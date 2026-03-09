# Trust Kernel API

The StegVerse Trust Kernel verifies execution authority before actions occur.

## Submit Intent

POST /intent

Example:

{
  "action": "repo.push",
  "target": "production"
}

## Retrieve Decision

GET /decision/{intent_id}

Returns:

{
  "decision": "allow | deny | defer"
}

## Verify Receipt

POST /verify_receipt
