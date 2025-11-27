# main.py
import threading
import time

from sensor.health_sensor import simulate_loop
from consumers.stream_consumer import run_simple_xread
from consumers.alerts_subscriber import run_subscriber
from analytics.analytics import display_loop
from indices.init_index import create_index


def start_sensor():
    simulate_loop(num_users=5, interval=0.5, iterations=999999)


def start_stream_consumer():
    run_simple_xread("$")


def start_alerts():
    run_subscriber()


def start_analytics():
    display_loop(interval=5)

def start_flask():
    from app import app
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    print("🔧 Creating index...")
    create_index()

    print("🚀 Starting system...")

    threads = [
        threading.Thread(target=start_sensor, daemon=True),
        threading.Thread(target=start_stream_consumer, daemon=True),
        threading.Thread(target=start_alerts, daemon=True),
        threading.Thread(target=start_analytics, daemon=True),
        threading.Thread(target=start_flask, daemon=True)

    ]

    # 啟動所有執行緒
    for t in threads:
        t.start()

    # 主程式保持存活
    while True:
        time.sleep(1)
