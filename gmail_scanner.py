import imaplib
import email
import os


def scan_gmail():
    email_address = os.environ.get("GMAIL_EMAIL")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not email_address or not app_password:
        return ["Gmail scanner is not configured."]

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_address, app_password)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")

        if status != "OK":
            return ["Unable to read Gmail inbox."]

        email_ids = messages[0].split()
        emails = []

        for e_id in email_ids[-5:]:
            status, msg_data = mail.fetch(e_id, "(RFC822)")

            if status != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg.get("subject", "(No Subject)")

            emails.append(subject)

        mail.logout()

        return emails

    except Exception as e:
        print("Gmail scanner error:", e)
        return ["Unable to connect to Gmail."]