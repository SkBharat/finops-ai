from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import os
import json
from chat_module import get_response, load_chat_history
from shutil import copyfile

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- Paths ----------
USER_FILE = "user.json"
DATA_DIR = "data"
CHART_DIR = os.path.join("static", "charts")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

# ---------- User Helpers ----------
def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump({}, f)
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

# ---------- Routes ----------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            flash("❌ Invalid credentials", "danger")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users:
            flash("⚠️ Username already exists", "warning")
        else:
            users[username] = password
            save_users(users)
            flash("✅ Account created! Please login.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    history = load_chat_history(username)
    chart = None

    if request.method == 'POST':
        user_message = request.form['message']
        response, chart_path = get_response(user_message, username)

        history.append({"role": "user", "content": user_message})
        history.append({"role": "bot", "content": response})

        # Save updated chat
        chat_file = os.path.join(DATA_DIR, f"{username}_chat.json")
        with open(chat_file, 'w') as f:
            json.dump(history, f)

        # Handle chart image
        if chart_path:
            chart_filename = os.path.basename(chart_path)
            final_chart = os.path.join(CHART_DIR, chart_filename)
            if not os.path.exists(final_chart):
                copyfile(chart_path, final_chart)
            chart = os.path.join("static", "charts", chart_filename)

    return render_template("index.html", username=username, history=history, chart=chart)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/download')
def download_csv():
    if 'username' not in session:
        return redirect(url_for('login'))

    file_path = os.path.join(DATA_DIR, f"{session['username']}_expenses.csv")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("⚠️ No CSV file found yet.", "info")
        return redirect(url_for('chat'))


@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    chat_file = os.path.join(DATA_DIR, f"{session['username']}_chat.json")
    if os.path.exists(chat_file):
        os.remove(chat_file)

    flash("✅ Chat cleared!", "info")
    return redirect(url_for('chat'))

# ---------- Run ----------
if __name__ == '__main__':
    app.run(debug=True)
