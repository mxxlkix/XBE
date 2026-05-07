from flask import Flask, render_template, redirect, request, session
import requests
import os

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_RANDOM"

CLIENT_ID = "1502014298602475761"
CLIENT_SECRET = "YOUR_SECRET"
REDIRECT_URI = "https://xbe-main.onrender.com/callback"

DISCORD_AUTH = "https://discord.com/oauth2/authorize"
DISCORD_API = "https://discord.com/api"

# ---------------- LANDING ----------------
@app.route("/")
def home():
    return render_template("index.html")

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

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify email"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    token_res = requests.post(
        f"{DISCORD_API}/oauth2/token",
        data=data,
        headers=headers
    ).json()

    access_token = token_res.get("access_token")

    user = requests.get(
        f"{DISCORD_API}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    session["user"] = user

    return redirect("/dashboard")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html", user=session["user"])

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
