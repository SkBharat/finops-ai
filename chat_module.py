import re
import os
import json
import pandas as pd
from smart_parser import SmartExpenseParser
from logger import log_expense
from insights import generate_category_spending_chart
from forecast import forecast_monthly_budget
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Load LLM
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
chat = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200)

# Smart parser
parser = SmartExpenseParser()

# Tips
SUGGESTIONS = {
    "Food": "🍽️ Eating out adds up fast. Try setting a weekly food budget, like ₹1500.",
    "Rent": "🏠 Keep rent under 30% of income. Good job logging fixed costs!",
    "Travel": "🚗 Consider using ride-sharing or public transport to cut down costs.",
    "Shopping": "🛍️ Stick to planned purchases. Use a wishlist to avoid impulse buys.",
    "Entertainment": "🎮 Enjoy your time! Just make sure it fits your budget goals.",
    "Other": "💡 Great! Tracking expenses regularly helps you build smarter habits."
}

# Chat history
CHAT_DIR = "chat_history"
os.makedirs(CHAT_DIR, exist_ok=True)

def get_chat_path(username):
    return os.path.join(CHAT_DIR, f"{username}.json")

def load_chat_history(username):
    path = get_chat_path(username)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_chat_history(username, history):
    with open(get_chat_path(username), "w") as f:
        json.dump(history, f, indent=2)

def ask_llm_finance_question(user_input):
    prompt = (
        "<|system|> You are FinOps AI, a helpful financial assistant. Answer clearly and briefly.\n"
        f"<|user|> {user_input}\n<|assistant|>"
    )
    result = chat(prompt)[0]['generated_text'].split("<|assistant|>")[-1].strip()
    return result, None

def get_response(user_input, username):
    history = load_chat_history(username)

    # Greeting
    if user_input.strip().lower() in {"hi", "hello", "hey", "hi!", "hello!", "hey!"}:
        suggestion = (
            "👋 Hey there! I’m your FinOps assistant.<br><br>"
            "**Here are some things I can help you with:**<br>"
            "- 💸 *Add a new expense*: `I spent ₹500 on lunch with Rahul`<br>"
            "- 📊 *Show spending chart*: `Show me my chart`<br>"
            "- 🔮 *Predict budget*: `Forecast my monthly budget`<br>"
            "- 📥 *Download log*: click the **📥 Download CSV** button<br><br>"
            "_Just type one to get started!_ 🚀"
        )
        history += [{"role": "user", "content": user_input}, {"role": "assistant", "content": suggestion}]
        save_chat_history(username, history)
        return suggestion, None

    # Summarization
    if re.search(r"summar(ize|y|ise).*?(spending|saving|expenses|finance|history)", user_input.lower()):
        combined = "\n".join([f"{m['role']}: {m['content']}" for m in history[-20:]])
        prompt = (
            "<|system|> You are FinOps AI, a finance-savvy assistant. Summarize the user's financial behavior and expenses based on the conversation history below.\n"
            f"<|user|>\n{combined}\n\nSummarize it clearly in 3-4 bullet points with financial tone.\n<|assistant|>"
        )
        summary = chat(prompt)[0]['generated_text'].split("<|assistant|>")[-1].strip()
        history += [{"role": "user", "content": user_input}, {"role": "assistant", "content": summary}]
        save_chat_history(username, history)
        return summary, None

    # Total spending
    if re.search(r"(how much|what).*?(spend|spent|total)", user_input.lower()):
        df_path = os.path.join("data", f"{username}_expenses.csv")
        if os.path.exists(df_path):
            df = pd.read_csv(df_path)
            total = df['amount'].sum()
            response = f"💰 You've spent a total of ₹{round(total, 2)} so far!"
        else:
            response = "⚠️ You haven't logged any expenses yet."
        history += [{"role": "user", "content": user_input}, {"role": "assistant", "content": response}]
        save_chat_history(username, history)
        return response, None

    # LLM Q&A
    if re.search(r"(what is|how do|how can|should i|explain|rule)", user_input.lower()):
        result, _ = ask_llm_finance_question(user_input)
        history += [{"role": "user", "content": user_input}, {"role": "assistant", "content": result}]
        save_chat_history(username, history)
        return result, None

    # Forecast
    if "predict" in user_input.lower() or "forecast" in user_input.lower():
        prediction = forecast_monthly_budget(username)
        history += [{"role": "user", "content": user_input}, {"role": "assistant", "content": prediction}]
        save_chat_history(username, history)
        return prediction, None

    # Chart
    if "chart" in user_input.lower() or "graph" in user_input.lower():
        chart_path = generate_category_spending_chart(username)
        message = "📊 Here's your spending chart below:" if chart_path else "⚠️ No data available to generate a chart yet."
        history += [{"role": "user", "content": user_input}, {"role": "assistant", "content": message}]
        save_chat_history(username, history)
        return (message, chart_path) if chart_path else (message, None)

    # Help with logging
    if re.search(r"(how|can|help|add).*?(expense|spending|log)", user_input.lower()):
        help_text = (
            "💡 To add an expense, just say something like:<br>"
            "`I spent ₹300 on groceries with Ayesha`<br>"
            "`Add ₹800 hostel rent with Karan`<br><br>"
            "I’ll take care of the rest! 😎"
        )
        history += [{"role": "user", "content": user_input}, {"role": "assistant", "content": help_text}]
        save_chat_history(username, history)
        return help_text, None

    # Parse and log expense
    parsed = parser.parse(user_input)
    if parsed["amount"] == 0.0 and parsed["category"] == "Other":
        warning = "🤔 That doesn't look like an expense. Try something like: `I spent ₹300 on food with Rahul`"
        history += [{"role": "user", "content": user_input}, {"role": "assistant", "content": warning}]
        save_chat_history(username, history)
        return warning, None

    log_expense(parsed, username)

    # Format response
    category = parsed['category']
    tip = SUGGESTIONS.get(category, SUGGESTIONS["Other"])
    amount = parsed['amount']
    people = ", ".join(parsed['people'])
    split = parsed['split']
    split_msg = "fully paid by you" if len(parsed['people']) == 1 else f"₹{split} each between {people}"

    smart_message = (
        f"✅ Logged ₹{amount} under *{category}*, split {split_msg}."
        f"<br><br>🧠 Tip: {tip}"
    )

    history += [{"role": "user", "content": user_input}, {"role": "assistant", "content": smart_message}]
    save_chat_history(username, history)

    return smart_message, None
