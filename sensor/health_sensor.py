import time
import json
import random
from datetime import datetime
from config.redis_client import get_redis

# 取得 Redis 連線
r = get_redis()

STREAM_KEY = "health:events"   # Redis Stream key
ALERT_CHANNEL = "alerts"       # Pub/Sub alert channel

def generate_sensor_payload(user_id: str):
    """產生模擬的感測器資料"""
    ts = int(time.time())  # Unix timestamp
    return {
        "user_id": user_id,
        "heart_rate": random.randint(55, 140),
        "bp_sys": random.randint(90, 190),
        "bp_dia": random.randint(50, 100),
        "temperature": round(36 + random.random() * 1.8, 1),
        "timestamp": ts
    }

def upload_payload_atomic(payload):
    """一次性上傳資料(atomic)：
       1) JSON.SET 最新資料
       2) XADD 加入 Stream
       3) ZADD 加入心跳歷史紀錄
    """
    user_id = payload["user_id"]
    ts = payload["timestamp"]

    pipe = r.pipeline(transaction=True)  # 啟動 Redis pipeline（原子操作）

    # 更新最新資料 (整個 JSON 寫入 .)
    pipe.execute_command(
        "JSON.SET", f"user:{user_id}:latest", ".", json.dumps(payload)
    )

    # 寫入 Stream（用於歷史處理）
    pipe.xadd(STREAM_KEY, fields=payload)

    # ZSET：紀錄心跳歷史，用 timestamp 當 score
    pipe.zadd(
        f"user:{user_id}:hr_zset",
        {json.dumps({"ts": ts, "hr": payload["heart_rate"]}): ts}
    )

    pipe.execute()  # 一次執行所有操作

def check_and_publish_alert(payload):
    """檢查是否超標 → 若有則 publish alert"""
    alerts = []
    if payload["heart_rate"] >= 120:
        alerts.append(f"High heart rate: {payload['heart_rate']}")
    if payload["bp_sys"] >= 160:
        alerts.append(f"High systolic BP: {payload['bp_sys']}")

    # 若有警報 → 發布 Pub/Sub 並寫入 Stream (health:alerts)
    if alerts:
        msg = {
            "user_id": payload["user_id"],
            "timestamp": payload["timestamp"],
            "alerts": alerts,
            "payload": payload
        }

        r.publish(ALERT_CHANNEL, json.dumps(msg))  # 發布即時警報
        r.xadd("health:alerts", fields={"user_id": payload["user_id"], "info": json.dumps(msg)})

def simulate_loop(num_users=3, interval=1.0, iterations=50):
    """模擬持續傳送感測器資料"""
    users = [f"user{n}" for n in range(1, num_users+1)]  # user1 ~ userN

    for _ in range(iterations):
        user = random.choice(users)  # 隨機選擇一位使用者
        payload = generate_sensor_payload(user)  # 產生假資料
        upload_payload_atomic(payload)           # 上傳
        check_and_publish_alert(payload)         # 判斷是否要發警報
        print(f"[{datetime.now().isoformat()}] Uploaded {payload}")
        time.sleep(interval)                     # 間隔秒數

if __name__ == "__main__":
    simulate_loop(num_users=5, interval=0.5, iterations=200)
