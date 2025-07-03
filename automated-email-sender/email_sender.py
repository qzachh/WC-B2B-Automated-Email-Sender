import csv
import smtplib
import time
import random
import os
from email.utils import make_msgid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- CONFIGURATION ---
SENDER_EMAIL    = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER     = 'smtp.gmail.com'
SMTP_PORT       = 465

ATTACHMENT_FILENAME = 'attachments/corporate_solution_teaser.pdf'
LOGO_IMAGE          = 'assets/logo.png'
BANNER_IMAGE        = 'assets/WeCare_signature.png'

MAX_EMAILS_PER_DAY  = 35
MIN_DELAY_SECONDS   = 180   # 3 minutes
MAX_DELAY_SECONDS   = 360   # 6 minutes

# --- Load Signature Template ---
with open('templates/signature.html', 'r', encoding='utf-8') as f:
    SIGNATURE_HTML = f.read()

# --- Load Email Templates ---
def load_template(template_name, name, company, gender):
    with open(f'templates/{template_name}.html', 'r', encoding='utf-8') as f:
        template = f.read()
    salutation = "Dear"
    if gender.lower() == "female":
        salutation += " Ms."
    elif gender.lower() == "male":
        salutation += " Mr."
    elif gender.lower() == "team":
        salutation += " Team"
    else:
        salutation += ""
    return template.format(salutation=salutation, name=name, company=company)

# --- Detect Company Type ---
def detect_company_type(company):
    industrial_keywords = ['manufacturing', 'factory', 'industrial', 'plant', 'production']
    for word in industrial_keywords:
        if word in company.lower():
            return 'industrial'
    return 'other'

# --- Send Email ---
def send_email(recipient_email, subject, html_body, attachment_path, logo_path, banner_path):
    msg = MIMEMultipart('related')
    msg['Message-ID'] = make_msgid(domain='example.com')
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    INVISIBLE_CHARS = ['\u200b', '\u200c', '\u200d', '\ufeff']
    suffix = ''.join(random.choice(INVISIBLE_CHARS) for _ in range(6))
    msg['Subject'] = subject + suffix

    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)
    msg_alternative.attach(MIMEText(html_body + SIGNATURE_HTML, 'html'))

    for cid, path in [('logo_img', logo_path), ('banner_img', banner_path)]:
        if path and os.path.isfile(path):
            with open(path, 'rb') as img:
                image = MIMEImage(img.read())
                image.add_header('Content-ID', f'<{cid}>')
                image.add_header('Content-Disposition', 'inline', filename=os.path.basename(path))
                msg.attach(image)

    if attachment_path and os.path.isfile(attachment_path):
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
        msg.attach(part)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email}")

# --- Main ---
def main():
    emails_sent = 0
    with open('data/contacts.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if emails_sent >= MAX_EMAILS_PER_DAY:
                print("Daily email limit reached.")
                break

            email   = row['email']
            name    = row['name']
            company = row['company']
            gender  = row['gender']

            template_type = 'healthcheck_template' if detect_company_type(company) == 'industrial' else 'staffing_template'
            body = load_template(template_type, name, company, gender)

            subject = f"Our Services for {company}"
            send_email(email, subject, body, ATTACHMENT_FILENAME, LOGO_IMAGE, BANNER_IMAGE)

            emails_sent += 1
            if emails_sent < MAX_EMAILS_PER_DAY:
                delay = random.randint(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                print(f"Waiting {delay // 60} min {delay % 60} sec before next email…")
                time.sleep(delay)

if __name__ == "__main__":
    main()
