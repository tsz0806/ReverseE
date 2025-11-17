# main.py

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import requests
import json
import uuid

# --- 1. 創建一個 FastAPI 應用實例 ---
# 這行代碼就像是聲明：「我要創建一個 API 服務了！」
app = FastAPI()

# --- 2. 你的「情報」配置 ---
# 這些是我們從瀏覽器開發者工具中偵測到的關鍵信息。
# 注意：這些信息（特別是 Cookie）可能會過期，如果失效需要重新獲取。

# API 端點和對話 ID
CONVERSATION_ID = "1a14ab89-a043-4f73-9a43-02515fccc7dd" 
API_URL = f"https://grok.ylsagi.com/rest/app-chat/conversations/{CONVERSATION_ID}/responses"

# 請求標頭，包含了你的身份信息 (Cookie) 和瀏覽器偽裝 (User-Agent)
HEADERS = {
    "Content-Type": "application/json",
    "Cookie": 'share_token=aaf6c70a7ba8832ae9b09ac055cd1081947d2d897b3ca2b65d826ceeecbcf653; imgID=67e253bdd0b63c582005f9a7; mp_ea93da913ddb66b6372b89d97b1029ac_mixpanel=%7B%22distinct_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%2C%22%24device_id%22%3A%229c284b9a-2aa5-4b8e-886e-78017fc21d9e%22%2C%22%24initial_referrer%22%3A%22https%3A%2F%2Fylsagi.com%2F%22%2C%22%24initial_referring_domain%22%3A%22ylsagi.com%22%2C%22__mps%22%3A%7B%7D%2C%22__mpso%22%3A%7B%7D%2C%22__mpus%22%3A%7B%7D%2C%22__mpa%22%3A%7B%7D%2C%22__mpu%22%3A%7B%7D%2C%22__mpr%22%3A%5B%5D%2C%22__mpap%22%3A%5B%5D%2C%22%24user_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%7D; i18nextLng=en',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
    "Origin": "https://grok.ylsagi.com",
    "Referer": "https://grok.ylsagi.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
    "x-xai-request-id": str(uuid.uuid4())
}

# 請求酬載（Payload）的模板
def build_payload(prompt: str):
    return {
        "message": prompt,
        "model": "grok-3",
        "parentResponseId": "f50ce991-0ab4-4a78-ba6d-440f7e628484", 
        # ... 其他從瀏覽器複製過來的參數
        "customPersonality": "",
        "disableArtifact": False,
        "isRegenRequest": False,
        "modelId": "grok-3",
        "modelMode": "MODEL_MODE_AUTO",
    }

# --- 3. 核心處理邏輯 ---
# 這是一個異步生成器函數，它負責：

    return StreamingResponse(stream_grok_response(dify_request_data), media_type="text/event-stream")
