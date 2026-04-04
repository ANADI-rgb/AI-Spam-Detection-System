phishing_keywords = [
"verify account",
"update password",
"bank login",
"paypal login",
"confirm identity",
"click link to verify",
"suspended account",
"security alert"
]

def detect_phishing(message):

    message = message.lower()

    for word in phishing_keywords:
        if word in message:
            return True

    return False