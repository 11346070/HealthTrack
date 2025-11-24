import time
import json
from datetime import datetime, timezone
from config.redis_client import get_redis

# 取得 Redis client
r = get_redis()

def get_hourly_avg(user_id: str, last_n_hours: int = 24):
    """
    取得指定 user 在最近 N 小時的平均心跳紀錄。
    資料來源：
      - ZSET 存小時索引 (analytics:hourly:{user})
      - String JSON 存每小時統計 (analytics:hour:{user}:{hour_key})
    """

    # 使用者的小時索引 ZSET key
    zkey = f"analytics:hourly:{user_id}"

    # 目前是第幾小時 (epoch 小時)
    now_hour = int(time.time() // 3600)

    # 從 ZSET 用 score 範圍撈出 hour_key（只取最近 N 小時）
    members = r.zrangebyscore(
        zkey,
        now_hour - last_n_hours + 1,
        now_hour
    )

    result = []

    # 根據每個 hour_key 去抓對應 JSON 統計資料
    for hour_key in members:
        raw = r.get(f"analytics:hour:{user_id}:{hour_key}")
        if raw:
            result.append(json.loads(raw))

    return result


def top_high_bp_users(n=10):
    """
    找出血壓最高的前 n 名使用者。
    資料來自 RedisJSON:
      user:*:latest
    """

    # 找出所有最新血壓資料的 key
    keys = r.keys("user:*:latest")
    results = []

    for key in keys:
        try:
            # RedisJSON 指令取得全部 JSON 資料
            raw = r.execute_command("JSON.GET", key, ".")
            data = json.loads(raw)

            # 存成 (key, bp_sys)
            results.append((key, float(data.get("bp_sys", 0))))
        except:
            continue

    # 依照血壓（bp_sys）由大到小排序
    results.sort(key=lambda x: -x[1])

    # 回傳前 n 名
    return [{"key": k, "bp_sys": v} for k, v in results[:n]]


def display_loop(users=None, interval=2):
    """
    每隔 interval 秒持續顯示 dashboard。
    包含：
      - 每位 user 的最近小時平均心跳
      - 血壓前 n 名
    """

    # 預設 5 個使用者
    if users is None:
        users = ["user1", "user2", "user3", "user4", "user5"]

    try:
        while True:
            print("\n--- Analytics ---")

            # 顯示每個使用者的小時統計
            for u in users:
                print(u, get_hourly_avg(u))

            # 顯示血壓最高的使用者
            print("Top BP:", top_high_bp_users())

            time.sleep(interval)

    except KeyboardInterrupt:
        print("Stopped Analytics Viewer")


if __name__ == "__main__":
    display_loop()
