from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from db import (
    verify_user,
    create_user,
    verify_admin,
    get_all_users,
    get_all_schedules,
    create_schedule,
    get_schedules_for_location,
    get_user_profile,
)

# Create the Flask application object. This is the central object used to
# register routes, configure settings, and run the web server.
app = Flask(__name__)

# A secret key is required for session handling and flash messages.
# In production, set `FLASK_SECRET` in the environment.
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")


@app.route("/")
def index():
    """Render the landing page with delivery schedules based on the logged-in user's area."""
    user = None
    schedule = get_all_schedules()
    schedule_label = "All areas"

    if session.get("user_id"):
        user = {"id": session.get("user_id"), "name": session.get("user_name")}
        profile = get_user_profile(session.get("user_id"))
        if profile and profile.get("user_address"):
            schedule = get_schedules_for_location(profile["user_address"])
            schedule_label = f"Your area ({profile['user_address']})"
        else:
            schedule = get_all_schedules()
            schedule_label = "All areas"

    return render_template(
        "index.html",
        schedule=schedule,
        schedule_label=schedule_label,
        user=user,
        page_class="landing-page",
    )


@app.context_processor
def inject_user():
    if session.get("user_id"):
        return {
            "current_user": {
                "id": session.get("user_id"),
                "name": session.get("user_name"),
                "role": session.get("user_role", "user"),
            }
        }
    return {"current_user": None}


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Render the sign-in page and handle sign-in submissions."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "user")

        if role == "admin":
            user = verify_admin(email, password)
        else:
            user = verify_user(email, password)

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user.get("name")
            session["user_role"] = "admin" if role == "admin" else "user"
            flash("Signed in successfully")
            return redirect(url_for("admin_dashboard") if role == "admin" else url_for("index"))

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
        address = request.form.get("address", "").strip()
        created = create_user(name, email, password, address)
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


@app.route("/admin/schedule", methods=["GET", "POST"])
def admin_schedule():
    """Allow admins to create delivery schedules for upcoming weeks."""
    if session.get("user_role") != "admin":
        flash("Admin access required")
        return redirect(url_for("signin"))

    if request.method == "POST":
        location = request.form.get("location", "").strip()
        delivery_time = request.form.get("delivery_time", "").strip()

        if location and delivery_time:
            created = create_schedule(location, delivery_time)
            if created:
                flash("Water delivery schedule created successfully")
            else:
                flash("Could not save the new schedule")
        else:
            flash("Please enter both the area and time")

        return redirect(url_for("admin_schedule"))

    schedules = get_all_schedules()
    return render_template("admin_schedule.html", schedules=schedules)


@app.route("/admin")
def admin_dashboard():
    """Render the admin dashboard showing all registered users."""
    if session.get("user_role") != "admin":
        flash("Admin access required")
        return redirect(url_for("signin"))

    users = get_all_users()
    return render_template("admin.html", users=users)


if __name__ == "__main__":
    # Start the Flask development server.
    # debug=True enables live reload and helpful error messages.
    app.run(debug=True)
