from flask import Flask, render_template, redirect, request, session
import requests

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_RANDOM_SECRET"

# ---------------------------
# DISCORD OAUTH CONFIG
# ---------------------------
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:10000/callback"

DISCORD_API = "https://discord.com/api"

# ---------------------------
# LANDING PAGE
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------
# LOGIN PAGE (BUTTON ONLY)
# ---------------------------
@app.route("/login")
def login():
    return render_template("login.html")


# ---------------------------
# DISCORD LOGIN REDIRECT
# ---------------------------
@app.route("/login/discord")
def login_discord():
    return redirect(
        f"{DISCORD_API}/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify%20email"
    )


# ---------------------------
# CALLBACK (CORE AUTH)
# ---------------------------
@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return "No code provided", 400

    # Exchange code for token
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify email"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_res = requests.post(
        f"{DISCORD_API}/oauth2/token",
        data=data,
        headers=headers
    )

    token_json = token_res.json()
    access_token = token_json.get("access_token")

    if not access_token:
        return f"Token error: {token_json}", 400

    # Get user info
    user_res = requests.get(
        f"{DISCORD_API}/users/@me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    user = user_res.json()

    # Save session
    session["user"] = {
        "id": user["id"],
        "username": user["username"],
        "global_name": user.get("global_name"),
        "avatar": user.get("avatar"),
        "email": user.get("email")
    }

    return redirect("/dashboard")


# ---------------------------
# DASHBOARD (PROTECTED)
# ---------------------------
@app.route("/dashboard")
def dashboard():
    user = session.get("user")

    if not user:
        return redirect("/login")

    return render_template("dashboard.html", user=user)


# ---------------------------
# LOGOUT
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
