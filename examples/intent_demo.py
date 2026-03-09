from stegverse.client import StegClient

client = StegClient()

intent = {
    "action": "compute.deploy",
    "target": "render.cluster",
}

intent_id = client.submit_intent(intent)

decision = client.get_decision(intent_id)

print(decision)
