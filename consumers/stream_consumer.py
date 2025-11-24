import time
import json
from datetime import datetime, timezone
from config.redis_client import get_redis

# 取得 redis 連線（假設 get_redis() 回傳 redis.Redis 物件）
r = get_redis()

# stream key 與 XREAD 的阻塞時間（毫秒）
STREAM_KEY = "health:events"
BLOCK_MS = 2000

def process_entry(entry_id, fields):
    # fields 來自 XREAD 的 entry 欄位映射（取 user_id, timestamp, heart_rate）
    user = fields.get("user_id")
    ts = int(fields.get("timestamp"))       # 事件的 unix timestamp（秒）
    hr = float(fields.get("heart_rate"))    # 心跳值（float）

    # 把 timestamp 轉成 YYYYmmddH 格式，當作「小時」分桶鍵（例如 2025010915）
    hour_key = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y%m%d%H")
    # epoch 小時數（可當作 sorted set 的 score）
    epoch_hour = ts // 3600

    # per-user per-hour 的聚合 hash key
    agg_hash = f"agg:hr:{user}:{hour_key}"

    # 使用 pipeline 一次送多個命令，提高效能
    pipe = r.pipeline()
    # 把 heart rate 加到 sum（浮點數累加）
    pipe.hincrbyfloat(agg_hash, "sum", hr)
    # count 加 1
    pipe.hincrby(agg_hash, "count", 1)
    # 設該聚合 key 在 48 小時後過期（避免無限累積）
    pipe.expire(agg_hash, 48 * 3600)
    pipe.execute()

    # 讀回 sum 與 count（注意：hget 回傳可能為 bytes 或 string，視 client 設定）
    sum_val = float(r.hget(agg_hash, "sum") or 0)
    count_val = int(r.hget(agg_hash, "count") or 0)
    # 計算平均心跳
    avg = sum_val / count_val if count_val else 0

    # 把 hour_key 加入 per-user 的 sorted set，score 使用 epoch 小時（方便按時間區間查詢）
    r.zadd(f"analytics:hourly:{user}", {hour_key: epoch_hour})
    # 把該小時的聚合結果用 JSON 存成一個 string key，方便快速讀取
    r.set(
        f"analytics:hour:{user}:{hour_key}",
        json.dumps({
            "hour": hour_key,
            "avg_hr": avg,
            "sum": sum_val,
            "count": count_val,
            "last_ts": ts
        })
    )

    # 日誌輸出，確認已處理
    print(f"[{datetime.now().isoformat()}] Processed {user} HR={hr} hour={hour_key}")

def run_simple_xread(last_id="$"):
    # 如果 last_id="$"：XREAD 只會回傳之後到達的新訊息（不會拉歷史）
    print("Starting stream consumer...")
    current_id = last_id
    while True:
        # 使用 XREAD 讀 stream，block 等待 BLOCK_MS 毫秒，最多一次取 50 筆
        resp = r.xread({STREAM_KEY: current_id}, block=BLOCK_MS, count=50)
        if not resp:
            # 若沒資料就繼續等待/迴圈（阻塞已處理等待）
            continue
        for stream_name, entries in resp:
            for entry_id, fields in entries:
                # 處理每一筆 entry
                process_entry(entry_id, fields)
                # 更新 current_id，下一次從這個 ID 後開始拉（避免重複處理同筆）
                current_id = entry_id

if __name__ == "__main__":
    run_simple_xread()
