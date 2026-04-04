from core.graph import agent_app

# Simulate a shipment delay message
inputs = {
    "incident_report": "Alert: SHIP_001 is experiencing a 48-hour delay due to weather.",
    "steps_taken": []
}

# Run the Agent!
print("🚀 Starting Supply Chain Agent...")
for output in agent_app.stream(inputs):
    for key, value in output.items():
        print(f"\n--- Node: {key} ---")
        if "steps_taken" in value:
            print(value["steps_taken"][-1])

print("\n✅ Final Investigation Complete.")