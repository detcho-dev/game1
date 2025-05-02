from flask import Flask, jsonify, render_template_string
import random as r

app = Flask(__name__)

# الصفحة الرئيسية
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
            </div>
        </div>

        <script>
            // إبدأ اللعبة
            function startGame() {
                fetch('/api/start_game')  // هنا بتعمل طلب لخادم فلاسك لبدء اللعبة
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById("balance").textContent = `Balance: $${data.balance}`;
                    })
                    .catch(err => {
                        console.error("Error:", err);
                    });
            }
        </script>

    </body>
    </html>
    """)

# API لبدء اللعبة
@app.route('/api/start_game')
def start_game():
    # هنا بتخصيص رصيد أولي للمستخدم
    balance = r.randint(500, 1000)  # رصيد عشوائي للمستخدم
    return jsonify(balance=balance)

if __name__ == '__main__':
    app.run(debug=True)
