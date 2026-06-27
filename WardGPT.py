from flask import Flask, request, redirect, session, render_template_string
import time
import random

app = Flask(__name__)
app.secret_key = "WARDGPT_SECRET_KEY"

# =========================
# USERS
# =========================
users = {
    "HaydenWard": "Hayd3nWard",
    "FinleyWard": "F1nleyWard",
    "RyanWard": "R9anWard",
    "JackieWard": "Jack1eWard",
    "GuestLogin": "GuestL0gin"
}

# =========================
# SYSTEM STORAGE
# =========================
muted = {}
banned = {}
chat_history = []

# =========================
# AI BRAIN
# =========================
def ai(msg, user):
    m = msg.lower()

    if any(x in m for x in ["hack", "steal", "attack"]):
        return "Woah, I can't help you with that. Go wash your head out and come back for another chat!"

    if "hello" in m:
        return f"Hello {user} 👋"
    if "joke" in m:
        return random.choice([
            "Why did the computer crash? Too many tabs!",
            "I told my RAM a joke… it forgot it instantly.",
            "Why did the CPU break up? Too many threads."
        ])
    if "python" in m:
        return "Python is used for AI, websites, automation, and more."
    if "time" in m:
        return time.strftime("%H:%M:%S")
    if "date" in m:
        return time.strftime("%d/%m/%Y")

    return "I'm WardGPT — I can answer questions, jokes, coding, and more."

# =========================
# MODERATION
# =========================
def is_muted(u):
    return u in muted and muted[u] > time.time()

def is_banned(u):
    return u in banned

# =========================
# LOGIN PAGE
# =========================
LOGIN_HTML = """
<body style="background:#0d0d0d;color:white;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;">

<div style="background:#1a1a1a;padding:30px;border-radius:10px;">
<h2>WardGPT Login</h2>

<form method="POST">
<input name="username" placeholder="Username"><br><br>
<input name="password" type="password" placeholder="Password"><br><br>
<button type="submit">Login</button>
</form>

</div>

</body>
"""

# =========================
# CHAT PAGE
# =========================
CHAT_HTML = """
<body style="margin:0;background:#0b0b0b;color:white;font-family:Arial;">

<div style="padding:10px;background:#1a1a1a;">
Logged in as {{user}}

{% if user == "HaydenWard" %}
<button onclick="location.href='/admin'">Admin Panel</button>
{% endif %}

<button onclick="location.href='/logout'">Logout</button>
</div>

<div style="padding:20px;height:75vh;overflow:auto;">
{% for c in chat %}
<p><b>{{c[0]}}:</b> {{c[1]}}</p>
{% endfor %}
</div>

<form method="POST" style="position:fixed;bottom:0;width:100%;display:flex;">
<input name="msg" style="flex:1;padding:15px;background:#1a1a1a;color:white;" placeholder="Type...">
<button style="padding:15px;">Send</button>
</form>

</body>
"""

# =========================
# ADMIN PAGE
# =========================
ADMIN_HTML = """
<body style="background:#0b0b0b;color:white;font-family:Arial;">

<h2>WardGPT Admin Panel</h2>

<h3>Users</h3>
<p>{{users}}</p>

<h3>Mute User</h3>
<form method="POST">
<input name="u" placeholder="Username">
<input name="t" placeholder="Minutes">
<button name="action" value="mute">Mute</button>
</form>

<h3>Ban User</h3>
<form method="POST">
<input name="u" placeholder="Username">
<button name="action" value="ban">Ban</button>
</form>

<h3>Recent Chats</h3>
{% for c in chat %}
<p>{{c}}</p>
{% endfor %}

</body>
"""

# =========================
# ROUTES
# =========================

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users and users[u] == p:
            session["user"] = u
            return redirect("/chat")

        return "Login failed"

    return LOGIN_HTML

# =========================
@app.route("/chat", methods=["GET","POST"])
def chat():
    if "user" not in session:
        return redirect("/")

    user = session["user"]

    if is_banned(user):
        return "You are banned."

    if request.method == "POST":
        msg = request.form["msg"]

        if is_muted(user):
            chat_history.append(("SYSTEM", f"{user} is muted"))
            return redirect("/chat")

        reply = ai(msg, user)

        chat_history.append((user, msg))
        chat_history.append(("WardGPT", reply))

    return render_template_string(CHAT_HTML, user=user, chat=chat_history[-30:])

# =========================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if session.get("user") != "HaydenWard":
        return "No access"

    if request.method == "POST":
        u = request.form.get("u")
        action = request.form.get("action")

        if action == "mute":
            try:
                t = int(request.form.get("t"))
                muted[u] = time.time() + t * 60
            except:
                pass

        if action == "ban":
            banned[u] = True

    return render_template_string(ADMIN_HTML, users=users.keys(), chat=chat_history[-20:])

# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================
if __name__ == "__main__":
    app.run(debug=True)
