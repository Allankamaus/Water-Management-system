from flask import Flask, render_template, request, redirect, url_for, flash

# Create the Flask application object. This is the central object used to
# register routes, configure settings, and run the web server.
app = Flask(__name__)

# A secret key is required for session handling and flash messages.
# In production, use a stronger secret key from an environment variable.
app.secret_key = "dev-secret"


@app.route("/")
def index():
    """Render the landing page with basic service information and delivery schedule."""
    # Example schedule data shown on the homepage. In later iterations,
    # this should come from a database or schedule service.
    schedule = [
        {"zone": "North", "date": "2026-06-20", "time": "08:00 - 10:00"},
        {"zone": "East", "date": "2026-06-21", "time": "14:00 - 16:00"},
    ]
    return render_template("index.html", schedule=schedule)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Render the sign-in page and handle sign-in submissions."""
    if request.method == "POST":
        # The POST submission currently acts as a placeholder.
        # In a real app, this is where you would verify the user's email and password.
        email = request.form.get("email")
        flash(f"Signed in (placeholder) as {email}")
        return redirect(url_for("index"))

    # For GET requests, just show the sign-in form.
    return render_template("signin.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Render the sign-up page and handle new account submissions."""
    if request.method == "POST":
        # The POST submission currently acts as a placeholder.
        # In a real app, create the new user record and store credentials.
        email = request.form.get("email")
        flash(f"Account created (placeholder) for {email}")
        return redirect(url_for("signin"))

    # For GET requests, show the sign-up form.
    return render_template("signup.html")


@app.route("/pay", methods=["GET", "POST"])
def pay():
    """Render the payment page and handle payment submissions."""
    if request.method == "POST":
        # The POST request is a placeholder payment flow.
        # Replace this with real payment processing code later.
        amount = request.form.get("amount")
        flash(f"Payment of {amount} received (placeholder)")
        return redirect(url_for("index"))

    # For GET requests, show the payment form.
    return render_template("pay.html")


if __name__ == "__main__":
    # Start the Flask development server.
    # debug=True enables live reload and helpful error messages.
    app.run(debug=True)
