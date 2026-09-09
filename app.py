from flask import Flask, render_template, request, redirect, session
import pickle
from datetime import datetime
import os

from auth import register_user, validate_user, reset_password
from explain_ai import analyze_message, highlight_text
from phishing_detector import detect_phishing
from gmail_scanner import scan_gmail


# --------------------------------------------------
# Flask App
# --------------------------------------------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "spam_ai_development_secret"
)


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "saved_model",
    "best_model.pkl"
)


# --------------------------------------------------
# Load Machine Learning Model
# --------------------------------------------------

try:
    with open(MODEL_PATH, "rb") as model_file:
        model = pickle.load(model_file)

    print("Spam detection model loaded successfully.")

except Exception as e:
    model = None
    print(f"Error loading model: {e}")


# --------------------------------------------------
# In-Memory Logs
# --------------------------------------------------

logs = []


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if validate_user(username, password):
            session["user"] = username
            return redirect("/")

        return "Invalid Login"

    return render_template("login.html")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/")
def index():

    if "user" not in session:
        return redirect("/login")

    return render_template("index.html")


# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    if "user" not in session:
        return redirect("/login")

    if model is None:
        return "Machine learning model could not be loaded.", 500

    message = request.form.get("message", "")
    file = request.files.get("email_file")

    # File upload
    if file and file.filename:
        try:
            message = file.read().decode("utf-8")
        except UnicodeDecodeError:
            return "Unable to read the uploaded file. Please upload a UTF-8 text file.", 400

    if not message.strip():
        return "Please enter a message or upload an email file.", 400

    # --------------------------------------------------
    # ML Prediction
    # --------------------------------------------------

    prediction = model.predict([message])[0]

    try:
        probability = model.predict_proba([message])[0][int(prediction)]
        confidence = round(float(probability) * 100, 2)
    except Exception:
        confidence = 0.0

    # --------------------------------------------------
    # AI Explanation
    # --------------------------------------------------

    spam_words, phishing_words = analyze_message(message)

    # --------------------------------------------------
    # Phishing Detection
    # --------------------------------------------------

    if phishing_words:
        result = "Phishing"

    elif prediction == 1:
        result = "Spam"

    else:
        result = "Not Spam"

    # --------------------------------------------------
    # Highlight Message
    # --------------------------------------------------

    highlighted_message = highlight_text(
        message,
        spam_words + phishing_words
    )

    # --------------------------------------------------
    # Store Logs
    # --------------------------------------------------

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


# --------------------------------------------------
# GMAIL SCANNER
# --------------------------------------------------

@app.route("/gmail")
def gmail():

    if "user" not in session:
        return redirect("/login")

    emails = scan_gmail()

    return render_template(
        "gmail.html",
        emails=emails
    )


# --------------------------------------------------
# ADMIN
# --------------------------------------------------

@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "admin.html",
        logs=logs
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


# --------------------------------------------------
# FORGOT PASSWORD
# --------------------------------------------------

@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    if request.method == "POST":

        username = request.form.get("username")
        new_password = request.form.get("new_password")

        success = reset_password(
            username,
            new_password
        )

        if success:
            return redirect("/login")

        return "User not found"

    return render_template("forgot.html")


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        success = register_user(
            username,
            password
        )

        if success:
            return redirect("/login")

        return "User already exists!"

    return render_template("register.html")


# --------------------------------------------------
# LOCAL DEVELOPMENT
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
