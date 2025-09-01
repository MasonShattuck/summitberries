# app.py — Summit Berries LLC
# -------------------------------------------------
# This Flask app serves your site and sends contact
# form submissions via Gmail SMTP (App Password).
#
# Environment variables required on Render:
#   SECRET_KEY      = a long random string
#   SMTP_SERVER     = smtp.gmail.com
#   SMTP_PORT       = 587
#   SMTP_USERNAME   = parkcityberries@gmail.com
#   SMTP_PASSWORD   = <your 16-char Gmail App Password>
#   TO_EMAIL        = parkcityberries@gmail.com  (or any inbox you want)
# -------------------------------------------------

import os
import smtplib, ssl
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__, static_folder="static", template_folder="templates")

# Secrets / SMTP config (from environment on Render)
app.secret_key  = os.getenv("SECRET_KEY", "dev-secret")
SMTP_SERVER     = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT       = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME   = os.getenv("SMTP_USERNAME")          # e.g., parkcityberries@gmail.com
SMTP_PASSWORD   = os.getenv("SMTP_PASSWORD")          # Gmail App Password
TO_EMAIL        = os.getenv("TO_EMAIL") or SMTP_USERNAME


def send_email(name: str, email: str, phone: str, message: str) -> None:
    """Send an inquiry email via Gmail SMTP with TLS."""
    if not (SMTP_USERNAME and SMTP_PASSWORD and TO_EMAIL):
        raise RuntimeError("SMTP credentials not configured")

    subject = "New Summit Berries Inquiry"
    body = (
        "New inquiry from Summit Berries website\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n\n"
        f"Message:\n{message}\n"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"]    = SMTP_USERNAME
    msg["To"]      = TO_EMAIL

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
        server.starttls(context=context)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


# --------- Health check for Render pings ----------
@app.route("/health")
def health():
    return jsonify(status="ok"), 200


# ------------------- Pages ------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = (request.form.get("name") or "").strip()
        email   = (request.form.get("email") or "").strip()
        phone   = (request.form.get("phone") or "").strip()
        message = (request.form.get("message") or "").strip()

        # Basic validation
        if not (name and email and message):
            flash("Please fill in your name, email, and message.", "warning")
            return redirect(url_for("contact"))

        try:
            send_email(name, email, phone, message)
            flash("Thanks! Your message was sent. We’ll get back to you shortly.", "success")
        except Exception:
            # For debugging locally you could: print(e)
            flash("Sorry—something went wrong sending your message. Please email us directly.", "danger")

        return redirect(url_for("home"))

    return render_template("contact.html")


# --------------- Local run ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
