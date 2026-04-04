import imaplib
import email

def scan_gmail():

    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    mail.login("your_email@gmail.com","your_app_password")

    mail.select("inbox")

    status, messages = mail.search(None, "ALL")

    email_ids = messages[0].split()

    emails = []

    for e_id in email_ids[-5:]:

        status, msg_data = mail.fetch(e_id, "(RFC822)")

        msg = email.message_from_bytes(msg_data[0][1])

        subject = msg["subject"]

        emails.append(subject)

    return emails