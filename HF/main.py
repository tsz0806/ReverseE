# main.py - 終極真相版 v2.1 

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import requests
import json
import uuid

app = FastAPI(title="Grok Mirror API v2.1")
# ... (CORSMiddleware 保持不變)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- 配置信息 ---
GROK_BASE_URL = "https://grok.ylsagi.com"

HEADERS = {
    "Content-Type": "application/json",
    # !! 重要 !! 請務必填寫你最新的有效 Cookie
    "Cookie": 'share_token=aaf6c70a7ba8832ae9b09ac055cd1081947d2d897b3ca2b65d826ceeecbcf653; imgID=67e253bdd0b63c582005f9a7; i18nextLng=en; mp_ea93da913ddb66b6372b89d97b1029ac_mixpanel=%7B%22distinct_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%2C%22%24device_id%22%3A%229c284b9a-2aa5-4b8e-886e-78017fc21d9e%22%2C%22%24initial_referrer%22%3A%22https%3A%2F%2Fylsagi.com%2F%22%2C%22%24initial_referring_domain%22%3A%22ylsagi.com%22%2C%22__mps%22%3A%7B%7D%2C%22__mpso%22%3A%7B%7D%2C%22__mpus%22%3A%7B%7D%2C%22__mpa%22%3A%7B%7D%2C%22__mpu%22%3A%7B%7D%2C%22__mpr%22%3A%5B%5D%2C%22__mpap%22%3A%5B%5D%2C%22%24user_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%7D',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
    "Origin": "https://grok.ylsagi.com",
    "Referer": "https://grok.ylsagi.com/",
}

# --- Pydantic 模型 (保持不變) ---
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "grok-3"
    conversation_id: Optional[str] = None
    parent_response_id: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# --- 輔助函數 (有修改) ---
def build_payload(message: str, model: str, parent_response_id: Optional[str] = None) -> dict:
    """根據是否有 parent_id 構建不同的 payload"""
    base_payload = {
        "message": message,
        "modelName": model, # 根據你捕獲的 payload，這裡用 modelName
        "modelMode": "MODEL_MODE_AUTO",
        # ... (複製你捕獲到的其他 payload 參數)
        "disableMemory": False,
        "disableSearch": False,
        "isReasoning": False,
    }
    if parent_response_id:
        # 如果是繼續對話，添加 parentResponseId
        base_payload["parentResponseId"] = parent_response_id
    return base_payload

def parse_streaming_response(response) -> Dict[str, Any]:
    """解析 Grok 的流式響應 (保持不變)"""
    full_response, response_id, conversation_id = "", None, None
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8'))
                if "result" in data:
                    result = data["result"]
                    if "token" in result and result["token"]:
                        full_response += result["token"]
                    # 關鍵：在流的最後，從 modelResponse 中捕獲 ID
                    if "modelResponse" in result:
                        model_resp = result["modelResponse"]
                        response_id = model_resp.get("responseId")
                        conversation_id = model_resp.get("conversationId") # 第一次請求的回應會包含 conv_id
            except (json.JSONDecodeError, KeyError):
                continue
    return {
        "response": full_response,
        "response_id": response_id,
        "conversation_id": conversation_id,
    }

# ========== API 路由 (核心修改) ==========
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """智能聊天端點，能自動判斷是新對話還是繼續對話"""
    try:
        if not request.message:
            return ChatResponse(success=False, error="Message is required")

        headers = HEADERS.copy()
        headers["x-xai-request-id"] = str(uuid.uuid4())
        
        is_new_conversation = not (request.conversation_id and request.parent_response_id)

        if is_new_conversation:
            # **情況一：開始一個新對話**
            # 使用我們新發現的 /new 端點
            url = f"{GROK_BASE_URL}/rest/app-chat/conversations/new"
            # Payload 不包含 parentResponseId
            payload = build_payload(request.message, request.model)
        else:
            # **情況二：繼續現有對話**
            # 使用舊的、帶有 conversation_id 的端點
            url = f"{GROK_BASE_URL}/rest/app-chat/conversations/{request.conversation_id}/responses"
            # Payload 包含 parentResponseId
            payload = build_payload(request.message, request.model, request.parent_response_id)

        # 發送請求
        response = requests.post(
            url, headers=headers, json=payload, stream=True, timeout=60
        )

        if response.status_code == 200:
            result = parse_streaming_response(response)
            
            # 從結果中獲取 conversation_id，如果是新對話，它會從伺服器返回
            # 如果是繼續對話，就用請求中傳入的 ID
            final_conv_id = result.get("conversation_id") or request.conversation_id

            return ChatResponse(
                success=True,
                data={
                    "response": result.get("response", ""),
                    "conversation_id": final_conv_id,
                    "response_id": result.get("response_id"),
                    "next_parent_response_id": result.get("response_id") # 為下次請求準備
                }
            )
        else:
            return ChatResponse(
                success=False,
                error=f"Request failed with status {response.status_code}",
                data={"details": response.text[:200]}
            )
            
    except Exception as e:
        return ChatResponse(success=False, error=f"An unexpected error occurred: {str(e)}")

# ... (其他如 /health, / 等端點可以保持不變)
