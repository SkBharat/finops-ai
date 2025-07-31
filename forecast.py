import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime
import os

def get_csv_file(username):
    return f"data/{username}_expenses.csv"

def forecast_monthly_budget(username):
    csv_file = get_csv_file(username)
    
    if not os.path.exists(csv_file):
        return "No data available for prediction yet."

    df = pd.read_csv(csv_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    now = datetime.now()

    # Filter for current month
    df = df[df['timestamp'].dt.month == now.month]
    if df.empty:
        return "No expenses logged this month."

    # Group by day and compute cumulative total
    df['day'] = df['timestamp'].dt.day
    df = df.groupby('day')['amount'].sum().cumsum().reset_index()

    X = df[['day']]
    y = df['amount']

    if len(X) < 2:
        return "Need more data to make a prediction."

    model = LinearRegression()
    model.fit(X, y)

    X_pred = pd.DataFrame([[30]], columns=['day'])
    predicted_amount = model.predict(X_pred)[0]
    predicted_amount = round(predicted_amount, 2)

    return f"📈 At this pace, you'll likely spend around ₹{predicted_amount} this month."
