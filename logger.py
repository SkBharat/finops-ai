import csv
import os

def get_csv_file(username):
    return f"data/{username}_expenses.csv"

def log_expense(data, username):
    """
    Appends structured expense data to a user-specific CSV file.
    Creates it with headers if it doesn't exist.

    data = {
        'amount': 600,
        'category': 'Food',
        'people': ['You', 'Rahul', 'Arjun'],
        'split': 200.0,
        'timestamp': '2025-06-24 18:30:00'
    }
    """
    filename = get_csv_file(username)
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # Make sure folder exists
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['timestamp', 'amount', 'category', 'people', 'split'])

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'timestamp': data['timestamp'],
            'amount': data['amount'],
            'category': data['category'],
            'people': ", ".join(data['people']),
            'split': data['split']
        })
