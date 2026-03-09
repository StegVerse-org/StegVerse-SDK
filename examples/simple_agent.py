from stegverse.client import StegClient

client = StegClient()

intent = {
    "action": "compute.deploy",
    "target": "gpu-cluster",
    "parameters": {"gpu": "A100"},
}

intent_id = client.submit_intent(intent)
decision = client.get_decision(intent_id)

if decision["decision"] == "allow":
    print("Execution permitted")
else:
    print("Execution blocked")
