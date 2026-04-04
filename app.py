from flask import Flask, render_template, request, redirect, session
import pickle
from datetime import datetime
import os

from auth import register_user, validate_user, reset_password
from explain_ai import analyze_message, highlight_text
from phishing_detector import detect_phishing
from gmail_scanner import scan_gmail

app = Flask(__name__)
app.secret_key = "spam_ai_secret"

# Load model
model_path = "saved_model/best_model.pkl"

if not os.path.exists(model_path):
    print("Model not found! Run model_training.py first.")
    exit()

model = pickle.load(open(model_path, "rb"))

# Store logs
logs = []

# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        if validate_user(username, password):
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid Login"

    return render_template("login.html")


# ---------------- DASHBOARD ---------------- #

@app.route('/')
def index():

    if 'user' not in session:
        return redirect('/login')

    return render_template("index.html")


# ---------------- PREDICTION (MAIN LOGIC) ---------------- #

@app.route("/predict", methods=["POST"])
def predict():

    if 'user' not in session:
        return redirect('/login')

    message = request.form.get("message")
    file = request.files.get("email_file")

    if file and file.filename != "":
        message = file.read().decode("utf-8")

    # ML prediction
    prediction = model.predict([message])[0]
    probability = model.predict_proba([message])[0][prediction]
    confidence = round(probability * 100, 2)

    # AI explanation
    spam_words, phishing_words = analyze_message(message)

    # Phishing check
    if phishing_words:
        result = "Phishing"
    elif prediction == 1:
        result = "Spam"
    else:
        result = "Not Spam"

    # Highlight text
    highlighted_message = highlight_text(message, spam_words + phishing_words)

    # Save logs
    logs.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": message[:50],
        "prediction": result,
        "confidence": confidence
    })

    return render_template(
        "index.html",
        prediction=result,
        confidence=confidence,
        highlighted=highlighted_message,
        spam_words=spam_words,
        phishing_words=phishing_words
    )


# ---------------- GMAIL SCANNER ---------------- #

@app.route("/gmail")
def gmail():

    if 'user' not in session:
        return redirect('/login')

    emails = scan_gmail()

    return render_template("gmail.html", emails=emails)


# ---------------- ADMIN ---------------- #

@app.route('/admin')
def admin():

    if 'user' not in session:
        return redirect('/login')

    return render_template("admin.html", logs=logs)


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():

    session.pop('user', None)
    return redirect('/login')

# ------------- FORGOT PASSWORD ------------ #

@app.route('/forgot', methods=['GET','POST'])
def forgot():

    if request.method == "POST":

        username = request.form['username']
        new_password = request.form['new_password']

        success = reset_password(username, new_password)

        if success:
            return redirect('/login')
        else:
            return "User not found"

    return render_template("forgot.html")

# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        success = register_user(username, password)

        if success:
            return redirect('/login')
        else:
            return "User already exists!"

    return render_template("register.html")

# ---------------- RUN APP ---------------- #

if __name__ == '__main__':
    app.run(debug=True)