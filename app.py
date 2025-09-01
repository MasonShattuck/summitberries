from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
# Health check endpoint for uptime pings
@app.route("/health", methods=["GET"])
def health():
    return "ok", 200
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
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        # For now, just print submissions to the terminal
        print(f"📩 New Inquiry: {name}, {email}, {phone}, {message}")

        return redirect(url_for("home"))  # after submitting, go back to home
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)

