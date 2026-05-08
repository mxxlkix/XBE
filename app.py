from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

import requests
import os

# ==================================================
# APP CONFIG
# ==================================================

app = Flask(__name__)

app.secret_key = "CHANGE_THIS_TO_RANDOM_SECRET"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///xbe.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ==================================================
# DATABASE
# ==================================================

db = SQLAlchemy(app)

# ==================================================
# DISCORD CONFIG
# ==================================================

CLIENT_ID = "1502014298602475761"

CLIENT_SECRET = "HO3Fo9gg0k-XNSNHDTvAP1D1_XoalW3M"

REDIRECT_URI = "https://discord.com/oauth2/authorize?client_id=1502014298602475761&response_type=code&redirect_uri=https%3A%2F%2Fxbe-main.onrender.com%2Fcallback&scope=identify+email+guilds"

DISCORD_AUTH = "https://discord.com/oauth2/authorize"

DISCORD_API = "https://discord.com/api"

# ==================================================
# USER MODEL
# ==================================================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    discord_id = db.Column(
        db.String(100),
        unique=True
    )

    username = db.Column(
        db.String(100)
    )

    avatar = db.Column(
        db.String(300)
    )

# ==================================================
# CREATE DATABASE
# ==================================================

with app.app_context():
    db.create_all()

# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return render_template("index.html")

# ==================================================
# LOGIN
# ==================================================

@app.route("/login")
def login():

    discord_login_url = (
        f"{DISCORD_AUTH}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=identify%20email%20guilds"
    )

    return redirect(discord_login_url)

# ==================================================
# CALLBACK
# ==================================================

@app.route("/callback")
def callback():

    code = request.args.get("code")

    if not code:
        return redirect("/")

    try:

        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "scope": "identify email guilds"
        }

        headers = {
            "Content-Type":
            "application/x-www-form-urlencoded"
        }

        token_response = requests.post(
            f"{DISCORD_API}/oauth2/token",
            data=data,
            headers=headers
        )

        token_json = token_response.json()

        access_token = token_json.get(
            "access_token"
        )

        if not access_token:
            return f"OAuth Error: {token_json}"

        # ==========================================
        # GET USER
        # ==========================================

        discord_user = requests.get(
            f"{DISCORD_API}/users/@me",
            headers={
                "Authorization":
                f"Bearer {access_token}"
            }
        ).json()

        # ==========================================
        # SAVE USER TO DATABASE
        # ==========================================

        existing_user = User.query.filter_by(
            discord_id=discord_user["id"]
        ).first()

        if not existing_user:

            new_user = User(
                discord_id=discord_user["id"],
                username=discord_user["username"],
                avatar=discord_user["avatar"]
            )

            db.session.add(new_user)
            db.session.commit()

        # ==========================================
        # SAVE SESSION
        # ==========================================

        session["user"] = {
            "id": discord_user["id"],
            "username": discord_user["username"],
            "avatar": discord_user["avatar"]
        }

        return redirect("/dashboard")

    except Exception as e:

        return f"Callback Error: {str(e)}"

# ==================================================
# DASHBOARD
# ==================================================

@app.route("/dashboard")
def dashboard():

    user = session.get("user")

    # DEV MODE
    if not user:

        user = {
            "id": "999999",
            "username": "Malik",
            "avatar": None
        }

    return render_template(
        "dashboard.html",
        user=user
    )

# ==================================================
# PROFILE
# ==================================================

@app.route("/profile")
def profile():

    user = session.get("user")

    db_user = User.query.filter_by(
        discord_id=user["id"]
    ).first()

    return render_template(
        "profile.html",
        user=db_user
    )

# ==================================================
# SERVERS
# ==================================================

@app.route("/servers")
def servers():

    return render_template("servers.html")

# ==================================================
# ANALYTICS
# ==================================================

@app.route("/analytics")
def analytics():

    return render_template(
        "analytics.html",
        total_users=User.query.count()
    )

# ==================================================
# SETTINGS
# ==================================================

@app.route("/settings")
def settings():

    return render_template("settings.html")

# ==================================================
# LIVE API
# ==================================================

@app.route("/api/live-stats")
def live_stats():

    total_users = User.query.count()

    return {
        "users": total_users
    }

# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ==================================================
# RUN APP
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=True
    )
