# Keywords that indicate spam
spam_keywords = [
    "free","win","winner","money","offer","click",
    "urgent","prize","lottery","cash","bonus"
]

# Keywords for phishing
phishing_keywords = [
    "verify","password","account","bank","login",
    "update","security","alert"
]

def analyze_message(message):

    message_lower = message.lower()

    found_spam = []
    found_phishing = []

    for word in spam_keywords:
        if word in message_lower:
            found_spam.append(word)

    for word in phishing_keywords:
        if word in message_lower:
            found_phishing.append(word)

    return found_spam, found_phishing


def highlight_text(message, keywords):

    words = message.split()

    highlighted = []

    for w in words:
        if w.lower().strip(".,!?") in keywords:
            highlighted.append(f"<mark>{w}</mark>")
        else:
            highlighted.append(w)

    return " ".join(highlighted)