# app.py — Summit Berries LLC
# Flask site + email via Gmail SMTP (App Password)

import os
import smtplib, ssl
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__, static_folder="static", template_folder="templates")

# ------------ Config (supports two naming schemes) ------------
# Prefer SMTP_* / TO_EMAIL if present; otherwise fall back to MAIL_* / CONTACT_RCPT
def _get(key_primary, fallback_key, default=None):
    v = os.getenv(key_primary)
    return v if v is not None else os.getenv(fallback_key, default)

app.secret_key  = os.getenv("SECRET_KEY", "dev-secret")          # set SECRET_KEY on Render

SMTP_SERVER     = _get("SMTP_SERVER",   "MAIL_SERVER",   "smtp.gmail.com")
SMTP_PORT       = int(_get("SMTP_PORT", "MAIL_PORT",     "587"))
SMTP_USERNAME   = _get("SMTP_USERNAME", "MAIL_USERNAME")         # e.g. parkcityberries@gmail.com
SMTP_PASSWORD   = _get("SMTP_PASSWORD", "MAIL_PASSWORD")         # 16-char Gmail App Password (no spaces)
TO_EMAIL        = _get("TO_EMAIL",      "CONTACT_RCPT") or SMTP_USERNAME


def send_email(name: str, email: str, phone: str, message: str) -> None:
    """Send an inquiry email via SMTP with STARTTLS."""
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
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"]    = SMTP_USERNAME
    msg["To"]      = TO_EMAIL

    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as s:
        s.starttls(context=ctx)
        s.login(SMTP_USERNAME, SMTP_PASSWORD)
        s.send_message(msg)

# ---------------- Health check for Render ----------------
@app.route("/health")
def health():
    return jsonify(status="ok"), 200

# ------------------------- Pages -------------------------
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
@app.route("/services/snow-removal")
def service_snow_removal():
    return render_template("snow_removal.html")

@app.route("/services/property-management")
def service_property_management():
    return render_template("property_management.html")

@app.route("/services/maintenance")
def service_maintenance():
    return render_template("maintenance.html")

@app.route("/services/pool-spa")
def service_pool_spa():
    return render_template("pool_spa.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = (request.form.get("name") or "").strip()
        email   = (request.form.get("email") or "").strip()
        phone   = (request.form.get("phone") or "").strip()
        message = (request.form.get("message") or "").strip()

        # basic validation
        if not (name and email and message):
            flash("Please fill in your name, email, and message.", "warning")
            return redirect(url_for("contact"))

        # simple honeypot (optional)
        if request.form.get("website"):
            # treated as spam; pretend success
            flash("Thanks! Your message was sent.", "success")
            return redirect(url_for("contact"))

        try:
            send_email(name, email, phone, message)
            flash("Thanks! Your message was sent. We’ll get back to you shortly.", "success")
        except Exception as e:
            app.logger.exception("Email send failed: %s", e)
            flash("Sorry—something went wrong sending your message. Please email us directly.", "danger")

        return redirect(url_for("contact"))

    return render_template("contact.html")


# ---------------------- Local run -----------------------

if __name__ == "__main__":
    app.run(debug=True, port=5001)
