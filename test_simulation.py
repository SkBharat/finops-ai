from chat_module import get_response

def simulate_chat(user, messages):
    print(f"\n=== Simulating chat for {user} ===")
    for msg in messages:
        print(f"> {msg}")
        response, _ = get_response(msg, user)
        print(response)

# Sample inputs
arjun_messages = [
    "hi",
    "I spent ₹500 on dinner with Rahul",
    "Show me my chart",
    "Forecast my monthly budget"
]

priya_messages = [
    "hello",
    "Add ₹900 hostel rent with Priya",
    "Show me my chart",
    "Forecast my monthly budget"
]

# Run simulation
simulate_chat("arjun", arjun_messages)
simulate_chat("priya", priya_messages)
