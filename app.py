from flask import Flask, render_template, request, redirect, session
import requests
import os

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_NEW_RANDOM_SECRET"

CLIENT_ID = "1502014298602475761"
CLIENT_SECRET = "HO3Fo9gg0k-XNSNHDTvAP1D1_XoalW3M"
REDIRECT_URI = "https://xbe-main.onrender.com/callback"

DISCORD_AUTH = "https://discord.com/oauth2/authorize"
DISCORD_API = "https://discord.com/api"

# ---------------- LANDING ----------------
@app.route("/")
def home():
    return redirect("/dashboard")

# ---------------- LOGIN (REDIRECT ONLY) ----------------
@app.route("/login")
def login():
    return redirect(
        f"{DISCORD_AUTH}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=identify%20email"
    )

# ---------------- CALLBACK ----------------
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
        }

        token = requests.post(
            "https://discord.com/api/oauth2/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ).json()

        access_token = token.get("access_token")

        if not access_token:
            return redirect("/")

        user = requests.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        session["user"] = {
            "id": user.get("id"),
            "username": user.get("username"),
        }

        return redirect("/dashboard")

    except:
        return redirect("/")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    fake_user = {
        "id": "123456789",
        "username": "Malik",
        "avatar": None
    }

    return render_template(
        "dashboard.html",
        user=fake_user
    )

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
