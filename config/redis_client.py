# config/redis_client.py
import redis 
import os    
from dotenv import load_dotenv    #防止資料外洩

load_dotenv()

def get_redis():
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        decode_responses=True,
        username=os.getenv("REDIS_USER"),
        password=os.getenv("REDIS_PASSWORD"),
    )

