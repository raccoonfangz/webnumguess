from flask import Flask, render_template_string, request, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

result_template = """
<!doctype html>
<html>
<head>
    <title>Game Result</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            text-align: center;
            background: #f0f0f0;
        }
        form {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1 id="result-message">{{ message|safe }}</h1>
    <form method="post" action="/reset">
        <button type="submit">Play Again</button>
    </form>


    <canvas id="confetti-canvas" style="position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>

    <script>
    // Only run confetti if message contains 'You won'
    const message = document.getElementById('result-message').innerHTML;
    if (message.includes('You won')) {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js';
        script.onload = () => {
            confetti({
                particleCount: 250,
                spread: 70,
                origin: { y: 0.6 }
            });
        };
        document.body.appendChild(script);
    }
    </script>
</body>
</html>
"""

html_template = """
<!doctype html>
<html>
<head>
    <title>Number Guesser</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            text-align: center;
            background: #f0f0f0;
        }
        form {
            margin-top: 20px;
        }
        input[type="text"], select, button {
            padding: 10px;
            font-size: 1rem;
            margin-top: 10px;
        }
        p, h1, h2 {
            margin: 10px 0;
        }
        .header {
            position: absolute;
            top: 20px;
            font-size: 2rem;
            font-weight: bold;
        }
        .footer {
            position: absolute;
            bottom: 10px;
            font-size: 0.9rem;
            color: #555;
        }
        .footer a {
            text-decoration: underline;
            color: inherit;
        }
    </style>
</head>
<body>
    <h1 class="header">Number Guesser</h1>
    {% if not session.get('game_started') %}
        <h2>Select your difficulty:</h2>
        <form method="post">
            <select name="difficulty">
                <option value="1">Easy (1–10) – 3 guesses</option>
                <option value="2">Medium (1–50) – 6 guesses</option>
                <option value="3">Hard (1–100) – 7 guesses</option>
            </select>
            <br>
            <button type="submit">Start Game</button>
        </form>
    {% else %}
        <h1>Guess the number between {{ session.bottom_limit }} and {{ session.upper_limit }}</h1>
        <p>Remaining guesses: {{ session.remaining_guesses }}</p>
        <form method="post">
            <input type="text" name="guess" placeholder="Enter your guess" required autocomplete="off">
            <br>
            <button type="submit">Guess</button>
        </form>
        {% if message %}
            <p>{{ message }}</p>
        {% endif %}
        <form method="post" action="/reset">
            <button type="submit">Reset Game</button>
        </form>
    {% endif %}
    <div class="footer">
        Made with love by <a href="https://ashton.bearblog.dev" target="_blank">Ashton</a>
    </div>
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''

    if request.method == 'POST':
        if not session.get('game_started'):
            difficulty = request.form.get('difficulty')
            if difficulty == '1':
                session['upper_limit'] = 10
                session['guess_limit'] = 3
            elif difficulty == '2':
                session['upper_limit'] = 50
                session['guess_limit'] = 6
            elif difficulty == '3':
                session['upper_limit'] = 100
                session['guess_limit'] = 7
            else:
                return render_template_string(html_template, message="Invalid difficulty")

            session['bottom_limit'] = 1
            session['number'] = random.randint(
                session['bottom_limit'], session['upper_limit'])
            session['remaining_guesses'] = session['guess_limit']
            session['game_started'] = True
        else:
            guess = request.form.get('guess')
            try:
                if guess is None:
                    message = "Error: No input provided. Please enter a valid number."
                else:
                    guess = int(float(guess))
                if guess < session['bottom_limit'] or guess > session['upper_limit']:
                    message = f"Error: Guess out of bounds ({session['bottom_limit']}-{session['upper_limit']})"
                else:
                    session['remaining_guesses'] -= 1
                    target = session['number']
                    if guess < target:
                        message = f"{guess} is too low. Higher ⬆︎"
                    elif guess > target:
                        message = f"{guess} is too high. Lower ⬇︎"
                    else:
                        session['final_message'] = f"🎉 You won! :D The number was {target}.<br>Guess attempts: {session['guess_limit'] - session['remaining_guesses']}"
                        session['game_started'] = False
                        return redirect(url_for('result'))

                    if session['remaining_guesses'] == 0:
                        session[
                            'final_message'] = f"Game over! You've used all your guesses.<br>The number was: {target}. Better luck next time!"
                        session['game_started'] = False
                        return redirect(url_for('result'))
            except ValueError:
                message = "Error: Please enter a valid number."

    return render_template_string(html_template, message=message)


@app.route('/result')
def result():
    message = session.get('final_message', '')
    return render_template_string(result_template, message=message)


@app.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
