from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import requests
import json
import uuid

app = FastAPI(
    title="Grok Mirror API",
    description="API proxy for Grok using correct endpoint",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 配置 ---
GROK_BASE_URL = "https://grok.ylsagi.com"

HEADERS = {
    "Content-Type": "application/json",
    "Cookie": 'share_token=aaf6c70a7ba8832ae9b09ac055cd1081947d2d897b3ca2b65d826ceeecbcf653; imgID=67e253bdd0b63c582005f9a7; i18nextLng=en; mp_ea93da913ddb66b6372b89d97b1029ac_mixpanel=%7B%22distinct_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%2C%22%24device_id%22%3A%229c284b9a-2aa5-4b8e-886e-78017fc21d9e%22%2C%22%24initial_referrer%22%3A%22https%3A%2F%2Fylsagi.com%2F%22%2C%22%24initial_referring_domain%22%3A%22ylsagi.com%22%2C%22__mps%22%3A%7B%7D%2C%22__mpso%22%3A%7B%7D%2C%22__mpus%22%3A%7B%7D%2C%22__mpa%22%3A%7B%7D%2C%22__mpu%22%3A%7B%7D%2C%22__mpr%22%3A%5B%5D%2C%22__mpap%22%3A%5B%5D%2C%22%24user_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%7D',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
    "Origin": "https://grok.ylsagi.com",
    "Referer": "https://grok.ylsagi.com/",
}

# --- 请求/响应模型 ---
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "grok-3"

class ChatResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# --- 构建请求负载（使用正确的格式）---
def build_payload(message: str, model: str = "grok-3") -> dict:
    """根据实际请求构建 payload"""
    return {
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
        "isReasoning": False,
        "message": message,
        "modelMode": "MODEL_MODE_AUTO",
        "modelName": model,
        "responseMetadata": {},
        "modelConfigOverride": {},
        "modelMap": {},
        "requestModelDetails": {
            "modelId": model
        },
        "returnImageBytes": False,
        "returnRawGrokInXaiRequest": False,
        "sendFinalMetadata": True,
        "temporary": False,
        "toolOverrides": {}
    }

# --- 解析流式响应 ---
def parse_streaming_response(response) -> Dict[str, Any]:
    """解析 Grok 的流式响应"""
    full_response = ""
    response_id = None
    conversation_id = None
    
    for line in response.iter_lines():
        if line:
            try:
                line_str = line.decode('utf-8')
                data = json.loads(line_str)
                
                if "result" in data:
                    result = data["result"]
                    
                    # 提取 token
                    if "token" in result and result["token"]:
                        full_response += result["token"]
                    
                    # 获取 IDs
                    if "responseId" in result:
                        response_id = result["responseId"]
                    
                    if "conversationId" in result:
                        conversation_id = result["conversationId"]
                    
                    # 检查是否结束
                    if result.get("isSoftStop", False):
                        break
                    
                    # 从 modelResponse 获取完整消息
                    if "modelResponse" in result:
                        model_resp = result["modelResponse"]
                        if "message" in model_resp:
                            full_response = model_resp["message"]
                        if "responseId" in model_resp:
                            response_id = model_resp["responseId"]
                        if "conversationId" in model_resp:
                            conversation_id = model_resp["conversationId"]
                            
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error parsing line: {e}")
    
    return {
        "response": full_response,
        "response_id": response_id,
        "conversation_id": conversation_id
    }

# ========== API 路由 ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Grok Mirror API",
        "version": "3.0.0",
        "status": "running",
        "endpoint": "/rest/app-chat/conversations/new",
        "note": "使用正确的 API 端点"
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "service": "grok-mirror-api"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天端点
    使用 /conversations/new 端点，每次都是新对话
    """
    try:
        if not request.message:
            return ChatResponse(success=False, error="Message is required")
        
        # 使用正确的端点
        url = f"{GROK_BASE_URL}/rest/app-chat/conversations/new"
        
        # 构建请求体
        payload = build_payload(request.message, request.model)
        
        # 准备请求头
        headers = HEADERS.copy()
        headers["x-xai-request-id"] = str(uuid.uuid4())
        headers["x-statsig-id"] = "JdqGp+hE6q0WsMpDDLRldv0O6ZNb+Mny24KLm/R/9pJdezRyT5a+PbxEdMFEOTVSTrW47iG05JO2DhUM3iJUk/pqbz4SJg"
        
        # 发送请求
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
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
                data={"details": response.text[:200]}
            )
            
    except requests.Timeout:
        return ChatResponse(
            success=False,
            error="Request timeout"
        )
    except Exception as e:
        return ChatResponse(
            success=False,
            error=f"Error: {str(e)}"
        )

@app.get("/test")
async def test():
    """测试端点"""
    return {
        "message": "API is working!",
        "correct_endpoint": "/rest/app-chat/conversations/new",
        "test": "Use POST /api/chat with {\"message\": \"Hello\"}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
