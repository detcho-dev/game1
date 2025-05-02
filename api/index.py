from flask import Flask, render_template, request, redirect, url_for, jsonify
import random as r
import json
import os

app = Flask(__name__)

users_file = "users.json"
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
            "password": None,
            "balance": 1000,
            "day": 1,
            "properties": [],
            "event_log": []
        }
        save_users(users)
    return users[username]

# جلب عرض شراء
def get_offer():
    ttype = r.choice(['land', 'property', 'gold', 'factory', 'company', 'island'])
    if ttype == 'land':
        price = r.randint(100, 500)
        return f"Land offer: Buy 1 plot for ${price}", {"type": ttype, "price": price}
    if ttype == 'property':
        price = r.randint(500, 2000)
        return f"Property offer: Buy 1 unit for ${price}", {"type": ttype, "price": price}
    if ttype == 'gold':
        grams = r.randint(10, 100)
        ppg = r.randint(50, 100)
        total = grams * ppg
        return f"Gold offer: {grams}g at ${ppg}/g for total ${total}", {"type": "gold", "grams": grams, "price_per_gram": ppg, "price": total}
    # إضافة عروض أخرى كما في الكود الأصلي
    return None, None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user['password'] is None:
            user['password'] = password
            save_users(load_users())
            return redirect(url_for('dashboard', username=username))
        elif user['password'] == password:
            return redirect(url_for('dashboard', username=username))
        else:
            return "Incorrect password", 403
    return render_template('login.html')

@app.route('/dashboard/<username>', methods=['GET', 'POST'])
def dashboard(username):
    user = get_user(username)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'buy':
            msg, data = get_offer()
            if msg:
                # Simulate buying process
                user['balance'] -= data['price']
                user['event_log'].append(f"Bought {data['type']} for ${data['price']}")
                save_users(load_users())
        elif action == 'daily_income':
            # Daily income processing
            user['balance'] += 100
            save_users(load_users())

    return render_template('dashboard.html', username=username, balance=user['balance'], event_log=user['event_log'])

if __name__ == '__main__':
    app.run(debug=True)
