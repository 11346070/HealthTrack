# HealthTrack — 即時健康監測系統

HealthTrack 是一套使用 **Redis Stream + Flask** 打造的即時健康監測系統。從資料輸入、處理、分析到警告通知，全流程串接如下：
```
感測器 → Redis Stream → 分析統計 → 警告推播 → Dashboard 即時呈現
```
本系統示範如何用 Redis 來處理即時資料，適合作為後端、資料流處理、分散式系統的 Side Project 展示。


## 🚀 功能 Features

- **Redis Streams：即時事件寫入 / 消費**
- **後端分析：小時平均、異常數據偵測**
- **Redis Pub/Sub 警告推播**
- **Flask Dashboard 即時呈現**
- **Jinja2 + JS 前端更新資料**


## 📦 安裝與執行方式 Installation

本專案使用者需要：

- Windows + **WSL Ubuntu**
- Ubuntu 內安裝 Redis
- 本地端 Python（建議 3.10+）


### 1️⃣ 安裝 WSL（如尚未安裝）

Windows PowerShell：

```
wsl --install
```

重開機後即可使用 Ubuntu。

---

### 2️⃣ 在 Ubuntu 安裝 Redis

```
sudo apt update
sudo apt install redis
```

啟動 Redis：

```
sudo service redis-server start
```

確認運作：

```
redis-cli ping
```

---

### 3️⃣ 建立 `.env`（⚠ 不會被上傳，請使用者自行建立）

在專案根目錄新增：

```
REDIS_HOST=
REDIS_PORT=
REDIS_USER=
REDIS_PASSWORD=
```

在vscode 終端機打上:

```
pip install python-dotenv

```

### 4️⃣ 啟動 Flask

```
python main.py
```

---

### 5️⃣ 開啟瀏覽器

```
http://127.0.0.1:5000/dashboard
```