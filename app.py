from flask import Flask, render_template, request, redirect, session, url_for
import json, os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return redirect(url_for('game'))

@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        answer = request.form.get('answer', '').lower()
        session['response'] = f"You said: {answer}"
        # Here you'll handle the logic of the game based on the answer
        return redirect(url_for('game'))

    message = session.get('message', 'Welcome to the Investor Game! Start playing.')
    response = session.get('response', '')
    return render_template('game.html', message=message, response=response)

if __name__ == '__main__':
    app.run(debug=True)
