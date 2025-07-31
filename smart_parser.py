# smart_parser.py

import re
import spacy
from difflib import get_close_matches
from datetime import datetime

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

# Category keywords
CATEGORIES = {
    "food": ["food", "lunch", "dinner", "breakfast", "snack", "meal"],
    "rent": ["rent", "hostel", "room", "accommodation", "housing", "lease"],
    "travel": ["travel", "bus", "uber", "auto", "taxi", "flight", "train", "transport"],
    "shopping": ["shopping", "clothes", "clothing", "cloth", "shoes", "accessories", "electronics", "mall"],
    "entertainment": ["entertainment", "netflix", "movie", "game", "concert", "event", "party"]
}

class SmartExpenseParser:
    def __init__(self):
        self.categories = CATEGORIES

    def extract_amount(self, text):
        match = re.search(r'(?:rs\.?|rupees|\u20B9)?\s?(\d{1,3}(?:,\d{3})*|\d+)(?:\.(\d{1,2}))?', text, re.IGNORECASE)
        if match:
            amt = match.group(0)
            amt = amt.replace("₹", "").replace(",", "").lower().replace("rs", "").replace("rupees", "").strip()
            return float(amt)
        return 0.0

    def extract_people(self, text):
        names = set()

        # spaCy person detection
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                names.add(ent.text.strip().title())

        # regex fallback: "with Rahul and Priya"
        matches = re.findall(r"with ([a-zA-Z ,]+)", text.lower())
        for match in matches:
            candidates = re.split(r"and|,", match)
            for name in candidates:
                name = name.strip().title()
                if name and name.lower() not in {"you", "me", "my", "i"}:
                    names.add(name)

        names.add("You")
        return list(names)

    def fuzzy_match_category(self, text):
        words = text.lower().split()
        for word in words:
            for cat, keywords in self.categories.items():
                match = get_close_matches(word, keywords, n=1, cutoff=0.8)
                if match:
                    return cat.title()
        return "Other"

    def parse(self, text):
        amount = self.extract_amount(text)
        category = self.fuzzy_match_category(text)
        people = self.extract_people(text)
        split = round(amount / len(people), 2) if people else amount
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "amount": amount,
            "category": category,
            "people": people,
            "split": split,
            "timestamp": timestamp
        }
