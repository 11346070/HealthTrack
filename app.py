import json
from flask import Flask, render_template,redirect
from analytics.analytics import get_hourly_avg, top_high_bp_users
from config.redis_client import get_redis


app = Flask(__name__)
r = get_redis()

USERS = ["user1", "user2", "user3", "user4", "user5"]

@app.route("/")
def index():
    return redirect("/dashboard")


@app.route("/dashboard")
def dashboard():
    # Top 10 BP
    top_bp = top_high_bp_users(10)

    # 最近 50 筆 alert
    alerts_raw = r.lrange("recent:alerts", 0, 9)
    alerts = [json.loads(a) for a in alerts_raw]

    return render_template(
        "dashboard.html",
        top_bp=top_bp,
        alerts=alerts,
    )
