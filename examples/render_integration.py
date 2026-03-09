from stegverse.client import StegClient

client = StegClient()

intent = {
    "action": "render.deploy",
    "target": "render.cluster",
    "parameters": {"gpu": "A100", "count": 4},
}

intent_id = client.submit_intent(intent)
print(client.get_decision(intent_id))
