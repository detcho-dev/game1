from flask import Flask, render_template, request, redirect, url_for, session
import time as t
import random as r
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # استخدم مفتاح سري للجلسات

users_file = "users.json"
units = {
    'land': 'meters',
    'property': 'units',
    'gold': 'grams',
    'factory': 'factories',
    'company': 'shares',
    'island': 'islands'
}


# طباعة مع توقف
def print_pause(message, delay=2):
    return message


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


# تحديث مستخدم
def update_user(username, data):
    users = load_users()
    users[username] = data
    save_users(users)


# تسجيل الدخول أو إنشاء حساب
def login(username):
    user = get_user(username)
    if user["password"]:
        return user
    else:
        return None


# دخل يومي
def daily_income(username):
    user = get_user(username)
    base_income = 100
    bonus = len(user["properties"]) * 50
    income = base_income + bonus
    user["balance"] += income
    user["event_log"].append(
        f"Daily income: ${income} (Base ${base_income} + ${bonus} bonus)")
    update_user(username, user)
    return f"Daily income: ${income}. Balance: ${user['balance']}"


# عرض شراء
def get_offer():
    ttype = r.choice(
        ['land', 'property', 'gold', 'factory', 'company', 'island'])
    if ttype == 'land':
        price = r.randint(100, 500)
        return f"Land offer: Buy 1 plot for ${price}", {
            "type": ttype,
            "price": price
        }
    if ttype == 'property':
        price = r.randint(500, 2000)
        return f"Property offer: Buy 1 unit for ${price}", {
            "type": ttype,
            "price": price
        }
    if ttype == 'gold':
        grams = r.randint(10, 100)
        ppg = r.randint(50, 100)
        total = grams * ppg
        return f"Gold offer: {grams}g at ${ppg}/g for total ${total}", {
            "type": "gold",
            "grams": grams,
            "price_per_gram": ppg,
            "price": total
        }
    if ttype == 'factory':
        capacity = r.randint(1, 5)
        price = capacity * r.randint(1000, 5000)
        return f"Factory offer: Buy factory with capacity {capacity} for ${price}", {
            "type": ttype,
            "capacity": capacity,
            "price": price
        }
    if ttype == 'company':
        shares = r.randint(10, 50)
        price_per_share = r.randint(200, 500)
        total = shares * price_per_share
        return f"Company offer: {shares} shares at ${price_per_share}/share for total ${total}", {
            "type": ttype,
            "shares": shares,
            "price_per_share": price_per_share,
            "price": total
        }
    # island
    size = r.choice(['small', 'medium', 'large'])
    multiplier = {'small': 500, 'medium': 2000, 'large': 5000}[size]
    price = multiplier * r.randint(1, 3)
    return f"Island offer: Buy a {size} island for ${price}", {
        "type": ttype,
        "size": size,
        "price": price
    }


# دمج الذهب بعنصر واحد
def merge_properties(username):
    user = get_user(username)
    merged = []
    gold_total = 0
    for item in user["properties"]:
        if item["type"] == 'gold':
            gold_total += item['grams']
        else:
            merged.append(item)
    if gold_total:
        merged.append({"type": "gold", "grams": gold_total, "spent": 0})
    user["properties"] = merged
    update_user(username, user)


# معالجة شراء
def handle_offer(username, data):
    user = get_user(username)
    price = data['price']
    choice = request.form.get('choice', 'no')
    if choice == 'negotiate':
        new_price = int(price * (1 - r.randint(5, 30) / 100))
        choice = 'yes'
        price = new_price
    if choice == 'yes':
        if user['balance'] >= price:
            user['balance'] -= price
            exists = False
            for item in user['properties']:
                if item['type'] == data['type']:
                    if data['type'] == 'gold': item['grams'] += data['grams']
                    elif data['type'] == 'company':
                        item['shares'] = item.get('shares', 0) + data['shares']
                    elif data['type'] == 'factory':
                        item['capacity'] = item.get('capacity',
                                                    0) + data['capacity']
                    else:
                        item['quantity'] = item.get('quantity', 0) + 1
                    item['spent'] += price
                    exists = True
            if not exists:
                entry = {'type': data['type'], 'spent': price}
                if data['type'] == 'gold': entry['grams'] = data['grams']
                elif data['type'] == 'company':
                    entry['shares'] = data['shares']
                elif data['type'] == 'factory':
                    entry['capacity'] = data['capacity']
                else:
                    entry['quantity'] = 1
                user['properties'].append(entry)
            user['event_log'].append(f"Bought {data['type']} for ${price}")
            update_user(username, user)
            return f"Purchased! New balance: ${user['balance']}"
        else:
            return "You don't have enough balance."
    else:
        return "No purchase made."


# الأحداث اليومية
def get_daily_events():
    return [
        r.choice(['offer', 'sell', 'auction']) for _ in range(r.randint(2, 5))
    ]


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = get_user(username)
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'income':
            result = daily_income(username)
        elif action == 'offer':
            msg, data = get_offer()
            result = handle_offer(username, data)
        else:
            result = "Invalid action."
        
        return render_template('index.html', user=user, result=result)

    return render_template('index.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and user["password"] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Invalid username or password"
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
