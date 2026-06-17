from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from db import verify_user, create_user

# Create the Flask application object. This is the central object used to
# register routes, configure settings, and run the web server.
app = Flask(__name__)

# A secret key is required for session handling and flash messages.
# In production, set `FLASK_SECRET` in the environment.
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")


@app.route("/")
def index():
    """Render the landing page with basic service information and delivery schedule."""
    # Example schedule data shown on the homepage. In later iterations,
    # this should come from a database or schedule service.
    schedule = [
        {"zone": "North", "date": "2026-06-20", "time": "08:00 - 10:00"},
        {"zone": "East", "date": "2026-06-21", "time": "14:00 - 16:00"},
    ]
    user = None
    if session.get("user_id"):
        user = {"id": session.get("user_id"), "name": session.get("user_name")}
    return render_template("index.html", schedule=schedule, user=user, page_class="landing-page")


@app.context_processor
def inject_user():
    if session.get("user_id"):
        return {"current_user": {"id": session.get("user_id"), "name": session.get("user_name")}}
    return {"current_user": None}


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Render the sign-in page and handle sign-in submissions."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = verify_user(email, password)
        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user.get("name")
            flash("Signed in successfully")
            return redirect(url_for("index"))
        flash("Invalid email or password")
        return redirect(url_for("signin"))

    # For GET requests, just show the sign-in form.
    return render_template("signin.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Render the sign-up page and handle new account submissions."""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        created = create_user(name, email, password)
        if created:
            flash("Account created. Please sign in.")
            return redirect(url_for("signin"))
        flash("Account already exists or error creating account")
        return redirect(url_for("signup"))

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


@app.route("/complaints", methods=["GET", "POST"])
def complaints():
    """Render the complaints page and handle complaint submissions."""
    if request.method == "POST":
        meter_id = request.form.get("meter_id")
        email = request.form.get("email")
        details = request.form.get("details")
        photo = request.files.get("photo")

        # Placeholder handling for complaint submissions.
        # In a later iteration, this should be stored or emailed to admins.
        flash("Your complaint has been submitted. Our admin team will review it shortly.")
        return redirect(url_for("complaints"))

    return render_template("complaints.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Signed out")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Start the Flask development server.
    # debug=True enables live reload and helpful error messages.
    app.run(debug=True)
