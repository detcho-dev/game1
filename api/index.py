from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to Investor Game!"

# ده الجزء المهم عشان Vercel يقدر يقرأ الـ app
def handler(request, response):
    return app(request, response)
