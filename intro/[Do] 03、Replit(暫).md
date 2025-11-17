<div align="center">

# 3️⃣ 以 Replit 為例的部署步驟（程式碼不變）

</div>

## 🟢 準備你的程式碼：

1. 將你的 FastAPI 程式碼保存為 `main.py`。

```python
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
# 1. 接收 Dify 的請求
# 2. 構造發往 Grok 鏡像網站的請求
# 3. 以流式方式接收 Grok 的數據，並一邊接收一邊轉發給 Dify
async def stream_grok_response(dify_request: dict):
    # 從 Dify 的請求中提取用戶的最新一條消息
    try:
        user_prompt = dify_request["messages"][-1]["content"]
    except (KeyError, IndexError):
        # 如果請求格式不對，返回錯誤信息
        error_message = {"error": {"message": "Invalid request format from Dify."}}
        yield f"data: {json.dumps(error_message)}\n\n"
        return

    # 構造發往 Grok 鏡像網站的 payload
    grok_payload = build_payload(user_prompt)
    
    # 更新 Headers 中的隨機請求 ID
    request_headers = HEADERS.copy()
    request_headers["x-xai-request-id"] = str(uuid.uuid4())

    try:
        # 使用 requests 庫發送流式請求
        with requests.post(API_URL, headers=request_headers, json=grok_payload, stream=True) as response:
            response.raise_for_status() # 檢查是否有 HTTP 錯誤
            
            # 遍歷從 Grok 鏡像網站返回的每一行流式數據
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    try:
                        data = json.loads(decoded_line)
                        token = data.get("result", {}).get("token", "")
                        
                        # 將提取到的 token 包裝成 Dify 能理解的 OpenAI SSE 格式
                        if token:
                            # 這是 OpenAI API 流式輸出的標準格式
                            sse_chunk = {
                                "id": f"chatcmpl-{uuid.uuid4()}",
                                "object": "chat.completion.chunk",
                                "created": int(uuid.uuid4().int >> 64), # 模擬時間戳
                                "model": "grok-3",
                                "choices": [{
                                    "index": 0,
                                    "delta": {"content": token},
                                    "finish_reason": None
                                }]
                            }
                            # 將這個數據塊發送給 Dify
                            yield f"data: {json.dumps(sse_chunk)}\n\n"

                    except json.JSONDecodeError:
                        continue # 忽略無法解析的行
            
            # 所有 token 都發送完畢後，發送一個結束標記
            end_chunk = {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion.chunk",
                "created": int(uuid.uuid4().int >> 64),
                "model": "grok-3",
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(end_chunk)}\n\n"
            yield "data: [DONE]\n\n"

    except requests.exceptions.RequestException as e:
        error_message = {"error": {"message": f"Failed to connect to Grok mirror: {e}"}}
        yield f"data: {json.dumps(error_message)}\n\n"

# --- 4. 創建 API 端點 ---
# @app.post(...) 告訴 FastAPI：
# 「當有人用 POST 方法訪問 /v1/chat/completions 這個路徑時，請執行下面的 chat_proxy 函數」
# 這個路徑是為了模仿 OpenAI 的 API，這樣 Dify 就能無縫對接。
@app.post("/v1/chat/completions")
async def chat_proxy(request: Request):
    dify_request_data = await request.json()
    # StreamingResponse 會調用我們的生成器函數，並將其產生的數據流式傳輸給客戶端（Dify）
    return StreamingResponse(stream_grok_response(dify_request_data), media_type="text/event-stream")
```

2. 創建一個 `requirements.txt` 檔案，裡面寫上所有需要的函式庫：
    ```txt
    fastapi
    uvicorn
    requests
    ```
3. （可選但推薦）創建一個 `runtime.txt` 檔案，指定 Python 版本，例如：
    ```txt
    python-3.11.4
    ```

## 🟢 **推送到 GitHub：**
    *   註冊一個 GitHub 帳號。
    *   創建一個新的倉庫 (Repository)。
    *   將你的 `main.py`、`requirements.txt` 和 `runtime.txt` 這幾個檔案上傳到這個倉庫。

## 🚀 **立即開始：Replit 快速部署**

### 步驟：
1. **訪問** [replit.com](https://replit.com)
2. **註冊/登入**（可用 Google/GitHub）
3. **Import to Replit** 
4. **從 GitHub 導入**：
   > 原本要先將 FastAPI 的檔案移到根目錄，但現在 Replit 的 AI Agent 功能很發達，他會自己讀完 Github 資料夾裡面的所有內容，然後自己不屬（超強！）
   
    ```text
    1. 選擇 "Import from GitHub"
    2. 貼上你的 repo URL：
       https://github.com/[你的用戶名]/ReverseE
    3. 選擇 Branch（通常是 main）
    4. 點擊 Import
    ```



