# main.py - 推荐版本（支持可选的对话记忆）


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import requests
import json
import uuid

app = FastAPI(
    title="Grok Mirror API",
    description="API proxy for Grok with optional conversation memory",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 配置信息 ---
GROK_BASE_URL = "https://grok.ylsagi.com"

HEADERS = {
    "Content-Type": "application/json",
    "Cookie": 'share_token=aaf6c70a7ba8832ae9b09ac055cd1081947d2d897b3ca2b65d826ceeecbcf653; imgID=67e253bdd0b63c582005f9a7; mp_ea93da913ddb66b6372b89d97b1029ac_mixpanel=%7B%22distinct_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%2C%22%24device_id%22%3A%229c284b9a-2aa5-4b8e-886e-78017fc21d9e%22%2C%22%24initial_referrer%22%3A%22https%3A%2F%2Fylsagi.com%2F%22%2C%22%24initial_referring_domain%22%3A%22ylsagi.com%22%2C%22__mps%22%3A%7B%7D%2C%22__mpso%22%3A%7B%7D%2C%22__mpus%22%3A%7B%7D%2C%22__mpa%22%3A%7B%7D%2C%22__mpu%22%3A%7B%7D%2C%22__mpr%22%3A%5B%5D%2C%22__mpap%22%3A%5B%5D%2C%22%24user_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%7D; i18nextLng=en',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
    "Origin": "https://grok.ylsagi.com",
    "Referer": "https://grok.ylsagi.com/",
}

# --- 请求/响应模型 ---
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "grok-3"
    conversation_id: Optional[str] = None
    parent_response_id: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# --- 创建新对话 ---
def create_new_conversation() -> Dict[str, str]:
    """创建新的 Grok 对话"""
    url = f"{GROK_BASE_URL}/rest/app-chat/conversations"
    headers = HEADERS.copy()
    headers["x-xai-request-id"] = str(uuid.uuid4())
    
    payload = {
        "title": "",
        "isFromGrokFiles": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            conv_id = data.get("conversationId") or data.get("conversation_id")
            first_resp_id = data.get("firstResponseId") or data.get("first_response_id")
            
            if conv_id and first_resp_id:
                return {
                    "conversation_id": conv_id,
                    "response_id": first_resp_id
                }
    except Exception as e:
        print(f"Error creating conversation: {e}")
    
    # 返回 None 表示创建失败
    return None

# --- 构建请求负载 ---
def build_payload(message: str, model: str, parent_response_id: str) -> dict:
    """构建发送到 Grok 的请求体"""
    return {
        "message": message,
        "model": model,
        "mode": "auto",
        "parentResponseId": parent_response_id,
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

# --- 解析流式响应 ---
def parse_streaming_response(response) -> Dict[str, Any]:
    """解析 Grok 的流式响应"""
    full_response = ""
    response_id = None
    
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
                    
                    # 获取 response ID
                    if "responseId" in result:
                        response_id = result["responseId"]
                    
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
                            
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error parsing line: {e}")
    
    return {
        "response": full_response,
        "response_id": response_id
    }

# ========== API 路由 ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Grok Mirror API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Single message mode (no conversation_id needed)",
            "Multi-turn conversation mode (pass conversation_id and parent_response_id)"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "chat": "/api/chat",
            "new_conversation": "/api/conversation/new"
        }
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "service": "grok-mirror-api"}

@app.post("/api/conversation/new")
async def new_conversation():
    """创建新对话（可选端点，用于手动创建对话）"""
    result = create_new_conversation()
    if result:
        return {
            "success": True,
            "data": result
        }
    else:
        return {
            "success": False,
            "error": "Failed to create new conversation"
        }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    智能聊天端点
    
    使用方式：
    1. 单次对话（无记忆）：只传 message
    2. 多轮对话（有记忆）：传 message + conversation_id + parent_response_id
    """
    try:
        if not request.message:
            return ChatResponse(success=False, error="Message is required")
        
        # 决定使用新对话还是继续对话
        if request.conversation_id and request.parent_response_id:
            # 继续现有对话
            conv_id = request.conversation_id
            parent_id = request.parent_response_id
            is_new_conversation = False
        else:
            # 创建新对话
            new_conv = create_new_conversation()
            if not new_conv:
                return ChatResponse(
                    success=False,
                    error="Failed to create new conversation"
                )
            conv_id = new_conv["conversation_id"]
            parent_id = new_conv["response_id"]
            is_new_conversation = True
        
        # 构建请求 URL
        url = f"{GROK_BASE_URL}/rest/app-chat/conversations/{conv_id}/responses"
        
        # 构建请求体
        payload = build_payload(request.message, request.model, parent_id)
        
        # 准备请求头
        headers = HEADERS.copy()
        headers["x-xai-request-id"] = str(uuid.uuid4())
        
        # 发送请求到 Grok
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
                    "conversation_id": conv_id,
                    "response_id": result.get("response_id"),
                    "is_new_conversation": is_new_conversation,
                    # 为下一次请求提供所需的参数
                    "next_parent_response_id": result.get("response_id")
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
        "usage": {
            "single_message": {
                "method": "POST",
                "url": "/api/chat",
                "body": {"message": "Hello"}
            },
            "multi_turn": {
                "method": "POST",
                "url": "/api/chat",
                "body": {
                    "message": "Continue conversation",
                    "conversation_id": "from_previous_response",
                    "parent_response_id": "from_previous_response"
                }
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
