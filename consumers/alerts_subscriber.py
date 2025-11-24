import json
from config.redis_client import get_redis

# 取得 Redis 連線
r = get_redis()

# 要訂閱的 channel
CHANNEL = "alerts"

def handle_alert_message(msg):
    """
    處理每一筆從 Pub/Sub 收到的訊息。
    將訊息解析為 JSON，並存入 recent:alerts list。
    """

    # 嘗試把訊息轉成 JSON，不行的話就原樣存
    try:
        payload = json.loads(msg)
    except:
        payload = {"raw": msg}

    # 把訊息推進 Redis list 的最前面
    r.lpush("recent:alerts", json.dumps(payload))

    # 只保留最新 200 筆資料 (index 0~199)
    r.ltrim("recent:alerts", 0, 199)

    # 輸出訊息內容
    print("ALERT RECEIVED:", payload)

def run_subscriber():
    """
    啟動 Redis Pub/Sub 訂閱者，監聽 alerts channel。
    """
    print("Subscribing to alerts...")

    # 建立 PubSub 物件，忽略訂閱系統訊息
    pubsub = r.pubsub(ignore_subscribe_messages=True)

    # 訂閱 alerts 頻道
    pubsub.subscribe(CHANNEL)

    # 持續等待訊息
    for message in pubsub.listen():
        # 只處理真正的 message 類型
        if message.get("type") == "message":
            # message["data"] 就是 publisher 發送的資料
            handle_alert_message(message["data"])

# 主程式入口
if __name__ == "__main__":
    run_subscriber()
