# main.py - 完整版本

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
import json
import uuid

# 創建 FastAPI 應用
app = FastAPI(
    title="Grok Mirror API",
    description="API proxy for Grok mirror service",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 配置信息 ---
CONVERSATION_ID = "1a14ab89-a043-4f73-9a43-02515fccc7dd"
API_URL = f"https://grok.ylsagi.com/rest/app-chat/conversations/{CONVERSATION_ID}/responses"

HEADERS = {
    "Content-Type": "application/json",
    "Cookie": 'share_token=aaf6c70a7ba8832ae9b09ac055cd1081947d2d897b3ca2b65d826ceeecbcf653; imgID=67e253bdd0b63c582005f9a7; mp_ea93da913ddb66b6372b89d97b1029ac_mixpanel=%7B%22distinct_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%2C%22%24device_id%22%3A%229c284b9a-2aa5-4b8e-886e-78017fc21d9e%22%2C%22%24initial_referrer%22%3A%22https%3A%2F%2Fylsagi.com%2F%22%2C%22%24initial_referring_domain%22%3A%22ylsagi.com%22%2C%22__mps%22%3A%7B%7D%2C%22__mpso%22%3A%7B%7D%2C%22__mpus%22%3A%7B%7D%2C%22__mpa%22%3A%7B%7D%2C%22__mpu%22%3A%7B%7D%2C%22__mpr%22%3A%5B%5D%2C%22__mpap%22%3A%5B%5D%2C%22%24user_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%7D; i18nextLng=en',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
    "Origin": "https://grok.ylsagi.com",
    "Referer": "https://grok.ylsagi.com/",
}

PARENTRESPONSEID = "324a5c10-d3e5-4a53-af7a-7baa4edac04b"

# --- 請求模型 ---
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "grok-3"

class ChatResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

# --- 構建請求負載 ---
def build_payload(prompt: str, model: str = "grok-3"):
    return {
        "message": prompt,
        "model": model,
        "mode": "auto",
        "parentResponseId": PARENTRESPONSEID,
        "customPersonality": "",
        "disableArtifact": False,
        "disableMemory": False,
        "disableSearch": False,
        "disableSelfHarmShortCircuit": False,
        "disableTextFollowUps": False,
        "enableImageGeneration": True,
        "enableImageStreaming": True,
        "enableSideBySide": True,
        "fileAttachments": [],
        "forceConcise": False,
        "forceSideBySide": False,
        "imageAttachments": [],
        "imageGenerationCount": 2,
        "isAsyncChat": False,
        "isFromGrokFiles": False,
        "isReasoning": False,
        "isRegenRequest": False,
        "metadata": {},
        "modelConfigOverride": {},
        "modelMap": {},
        "request_metadata": {
            "mode": "auto",
            "model": model
        },
        "requestModelDetails": {
            "modelId": model,
            "modelMode": "MODEL_MODE_AUTO",
            "modelName": model
        },
        "returnImageBytes": False,
        "returnRawGrokInXaiRequest": False,
        "sendFinalMetadata": True,
        "skipCancelCurrentInflightRequests": False,
        "toolOverrides": {}
    }

# --- 解析流式響應 ---
def parse_streaming_response(response):
    """解析 Grok 的流式響應"""
    full_response = ""
    response_id = None
    
    for line in response.iter_lines():
        if line:
            try:
                line_str = line.decode('utf-8')
                data = json.loads(line_str)
                
                if "result" in data:
                    result = data["result"]
                    
                    # 提取 token（實際的回應內容）
                    if "token" in result and result["token"]:
                        full_response += result["token"]
                    
                    # 獲取響應 ID
                    if "responseId" in result:
                        response_id = result["responseId"]
                    
                    # 檢查是否結束
                    if result.get("isSoftStop", False):
                        break
                    
                    # 獲取完整的模型響應
                    if "modelResponse" in result:
                        model_resp = result["modelResponse"]
                        if "message" in model_resp:
                            full_response = model_resp["message"]
                        if "responseId" in model_resp:
                            response_id = model_resp["responseId"]
                            
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error parsing line: {e}")
    
    return {
        "response": full_response,
        "response_id": response_id,
        "conversation_id": CONVERSATION_ID
    }

# ========== API 路由 ==========

@app.get("/")
async def root():
    """根路徑 - API 信息"""
    return {
        "name": "Grok Mirror API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "chat": "/api/chat"
        }
    }

@app.get("/health")
async def health():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "grok-mirror-api",
        "conversation_id": CONVERSATION_ID
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    主要的聊天端點
    
    接收用戶消息，轉發到 Grok 鏡像，返回回應
    """
    try:
        if not request.message:
            return ChatResponse(
                success=False,
                error="Message is required"
            )
        
        # 構建請求
        payload = build_payload(request.message, request.model)
        headers = HEADERS.copy()
        headers["x-xai-request-id"] = str(uuid.uuid4())
        
        # 發送請求到 Grok 鏡像
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            # 解析流式響應
            result = parse_streaming_response(response)
            
            if not result.get("response"):
                return ChatResponse(
                    success=False,
                    error="No response received from Grok"
                )
            
            return ChatResponse(
                success=True,
                data={
                    "response": result.get("response", ""),
                    "conversation_id": result.get("conversation_id"),
                    "response_id": result.get("response_id")
                }
            )
        else:
            return ChatResponse(
                success=False,
                error=f"Request failed with status {response.status_code}",
                data={"details": response.text}
            )
            
    except requests.Timeout:
        return ChatResponse(
            success=False,
            error="Request timeout - Grok API took too long to respond"
        )
    except requests.RequestException as e:
        return ChatResponse(
            success=False,
            error=f"Request error: {str(e)}"
        )
    except Exception as e:
        return ChatResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

@app.get("/test")
async def test():
    """快速測試端點"""
    return {
        "message": "API is working!",
        "test_chat": "Use POST /api/chat with body: {\"message\": \"your message\"}"
    }

# 本地測試用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
