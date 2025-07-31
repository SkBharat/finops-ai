import pandas as pd
from matplotlib import pyplot as plt
import os

def get_csv_file(username):
    return f"data/{username}_expenses.csv"

def generate_category_spending_chart(username):
    """
    Generates a bar chart of total spending per category from the user's CSV.
    Saves and returns the chart image path.
    """
    csv_file = get_csv_file(username)
    if not os.path.exists(csv_file):
        print("No expense data found.")
        return None

    df = pd.read_csv(csv_file)

    # Group by category and sum
    category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)

    # Plotting
    plt.figure(figsize=(8, 4))
    category_totals.plot(kind='bar', color='skyblue')
    plt.title('Total Spending by Category')
    plt.xlabel('Category')
    plt.ylabel('Total Amount (₹)')
    plt.tight_layout()

    # Save user-specific chart
    output_file = f"data/{username}_category_spending.png"
    plt.savefig(output_file)
    plt.close()

    return output_file
