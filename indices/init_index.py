from config.redis_client import get_redis
from redis.commands.search.field import TextField, NumericField
from redis.commands.search.index_definition import IndexDefinition, IndexType

# 建立 Redis client（連線）
r = get_redis()
INDEX_NAME = "idx_health"        # RediSearch Index 名稱

def create_index():
    try:
		# 嘗試取得 index 資訊 -- 如果成功代表 Index 已存在
        r.ft(INDEX_NAME).info()
        print("Index already exists.")
        return
    except Exception:
		# info() 出錯 → Index 尚未存在 → 要建立
        print("Creating new index...")
        
	# RediSearch schema：定義可搜尋的 JSON 欄位
    schema = (
        TextField("$.user_id", as_name="user_id"),           # JSON 中的 name 欄位
        NumericField("$.heart_rate", as_name="heart_rate"),
        NumericField("$.bp_sys", as_name="bp_sys"),
        NumericField("$.bp_dia", as_name="bp_dia"),
        NumericField("$.temperature", as_name="temperature"),
        NumericField("$.timestamp", as_name="timestamp")
    )
		
	# 建立 JSON Index，prefix=user: 表示只索引 user: 開頭的 key
    r.ft(INDEX_NAME).create_index(
        fields=schema,
        definition=IndexDefinition(prefix=["user:"], index_type=IndexType.JSON)
    )

    print("Index created!")

# 如果直接執行檔案 → 自動建立 Index
if __name__ == "__main__":
    create_index()
