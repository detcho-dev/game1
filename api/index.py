from flask import Flask, jsonify, render_template_string, request
import random as r
import json
import os

app = Flask(__name__)

# المسار الخاص بملف بيانات المستخدمين
users_file = "users.json"

# وحدات اللعبة
units = {
    'land': 'meters',
    'property': 'units',
    'gold': 'grams',
    'factory': 'factories',
    'company': 'shares',
    'island': 'islands'
}

# تحميل وحفظ بيانات المستخدمين
def load_users():
    if not os.path.exists(users_file):
        with open(users_file, 'w') as f:
            json.dump({}, f)
    with open(users_file, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=4)

# جلب مستخدم أو إنشاء جديد
def get_user(username):
    users = load_users()
    if username not in users:
        users[username] = {
            "balance": 1000,
            "day": 1,
            "properties": [],
            "event_log": []
        }
        save_users(users)
    return users[username]

# تحديث المستخدم
def update_user(username, data):
    users = load_users()
    users[username] = data
    save_users(users)

# لعبة المستثمر - API
@app.route('/api/start_game')
def start_game():
    # بدء اللعبة مع رصيد أولي
    username = request.args.get('username', 'guest')
    user = get_user(username)
    balance = user["balance"]
    return jsonify(balance=balance)

@app.route('/api/daily_income')
def daily_income():
    username = request.args.get('username', 'guest')
    user = get_user(username)
    base_income = 100
    bonus = len(user["properties"]) * 50
    income = base_income + bonus
    user["balance"] += income
    user["event_log"].append(f"Daily income: ${income} (Base ${base_income} + ${bonus} bonus)")
    update_user(username, user)
    return jsonify(balance=user["balance"], income=income)

# صفحة الواجهة الرئيسية
@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Investor Game</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">

        <div class="flex justify-center items-center min-h-screen">
            <div class="bg-white p-8 rounded-lg shadow-lg w-96">
                <h1 class="text-3xl font-bold text-center text-green-600 mb-6">Welcome to Investor Game</h1>
                <p id="balance" class="text-xl text-center mb-4">Balance: $0</p>
                <button onclick="startGame()" class="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 transition duration-300">Start Game</button>
                <button onclick="dailyIncome()" class="w-full bg-yellow-500 text-white py-2 mt-4 rounded-md hover:bg-yellow-600 transition duration-300">Claim Daily Income</button>
            </div>
        </div>

        <script>
            let username = 'guest';  // يمكن تغيير هذا لاحقًا لجعل المستخدم يسجل دخوله

            // بدء اللعبة
            function startGame() {
                fetch(`/api/start_game?username=${username}`)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById("balance").textContent = `Balance: $${data.balance}`;
                    })
                    .catch(err => {
                        console.error("Error:", err);
                    });
            }

            // استلام الدخل اليومي
            function dailyIncome() {
                fetch(`/api/daily_income?username=${username}`)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById("balance").textContent = `Balance: $${data.balance}`;
                        alert(`You earned $${data.income} today!`);
                    })
                    .catch(err => {
                        console.error("Error:", err);
                    });
            }
        </script>

    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(debug=True)
