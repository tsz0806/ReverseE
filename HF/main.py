from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import requests
import json
import uuid
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Grok Mirror API",
    version="3.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROK_BASE_URL = "https://grok.ylsagi.com"

HEADERS = {
    "Content-Type": "application/json",
    "Cookie": 'share_token=aaf6c70a7ba8832ae9b09ac055cd1081947d2d897b3ca2b65d826ceeecbcf653; imgID=67e253bdd0b63c582005f9a7; i18nextLng=en; mp_ea93da913ddb66b6372b89d97b1029ac_mixpanel=%7B%22distinct_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%2C%22%24device_id%22%3A%229c284b9a-2aa5-4b8e-886e-78017fc21d9e%22%2C%22%24initial_referrer%22%3A%22https%3A%2F%2Fylsagi.com%2F%22%2C%22%24initial_referring_domain%22%3A%22ylsagi.com%22%2C%22__mps%22%3A%7B%7D%2C%22__mpso%22%3A%7B%7D%2C%22__mpus%22%3A%7B%7D%2C%22__mpa%22%3A%7B%7D%2C%22__mpu%22%3A%7B%7D%2C%22__mpr%22%3A%5B%5D%2C%22__mpap%22%3A%5B%5D%2C%22%24user_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%7D',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
    "Origin": "https://grok.ylsagi.com",
    "Referer": "https://grok.ylsagi.com/",
}

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "grok-3"

class ChatResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

def build_payload(message: str, model: str = "grok-3") -> dict:
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

def parse_streaming_response(response) -> Dict[str, Any]:
    """改进的解析函数，带调试日志"""
    full_response = ""
    response_id = None
    conversation_id = None
    line_count = 0
    
    logger.info("开始解析流式响应...")
    
    try:
        for line in response.iter_lines():
            if line:
                line_count += 1
                try:
                    line_str = line.decode('utf-8')
                    
                    # 记录前5行用于调试
                    if line_count <= 5:
                        logger.info(f"Line {line_count}: {line_str[:200]}")
                    
                    data = json.loads(line_str)
                    
                    if "result" in data:
                        result = data["result"]
                        
                        # 提取 token
                        token = result.get("token")
                        if token:
                            full_response += token
                            logger.debug(f"Added token: {token}")
                        
                        # 获取 IDs
                        if "responseId" in result:
                            response_id = result["responseId"]
                            logger.debug(f"Got responseId: {response_id}")
                        
                        if "conversationId" in result:
                            conversation_id = result["conversationId"]
                            logger.debug(f"Got conversationId: {conversation_id}")
                        
                        # 检查完整响应
                        if "modelResponse" in result:
                            model_resp = result["modelResponse"]
                            msg = model_resp.get("message")
                            if msg:
                                full_response = msg
                                logger.info(f"Got full message from modelResponse: {msg[:100]}")
                            
                            if "responseId" in model_resp:
                                response_id = model_resp["responseId"]
                            if "conversationId" in model_resp:
                                conversation_id = model_resp["conversationId"]
                        
                        # 检查是否结束
                        if result.get("isSoftStop", False):
                            logger.info("Received soft stop signal")
                            break
                
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON decode error on line {line_count}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error parsing line {line_count}: {e}")
                    continue
        
        logger.info(f"Parsing completed. Total lines: {line_count}, Response length: {len(full_response)}")
        
    except Exception as e:
        logger.error(f"Error during iteration: {e}")
    
    return {
        "response": full_response,
        "response_id": response_id,
        "conversation_id": conversation_id,
        "debug_line_count": line_count
    }

@app.get("/")
async def root():
    return {
        "name": "Grok Mirror API",
        "version": "3.1.0",
        "status": "running",
        "debug": "Check /logs for detailed logging"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天端点（带调试日志）"""
    try:
        if not request.message:
            return ChatResponse(success=False, error="Message is required")
        
        logger.info(f"收到请求: {request.message}")
        
        # 使用 /conversations/new 端点
        url = f"{GROK_BASE_URL}/rest/app-chat/conversations/new"
        
        # 构建请求
        payload = build_payload(request.message, request.model)
        
        headers = HEADERS.copy()
        headers["x-xai-request-id"] = str(uuid.uuid4())
        headers["x-statsig-id"] = "JdqGp+hE6q0WsMpDDLRldv0O6ZNb+Mny24KLm/R/9pJdezRyT5a+PbxEdMFEOTVSTrW47iG05JO2DhUM3iJUk/pqbz4SJg"
        
        logger.info(f"发送请求到: {url}")
        
        # 发送请求
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=60
        )
        
        logger.info(f"收到响应，状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = parse_streaming_response(response)
            
            logger.info(f"解析结果: response_length={len(result.get('response', ''))}, line_count={result.get('debug_line_count', 0)}")
            
            if not result.get("response"):
                # 如果没有响应，返回调试信息
                return ChatResponse(
                    success=False,
                    error="No response received from Grok",
                    data={
                        "debug_info": {
                            "lines_processed": result.get("debug_line_count", 0),
                            "response_id": result.get("response_id"),
                            "conversation_id": result.get("conversation_id"),
                            "hint": "Check Hugging Face Logs for details"
                        }
                    }
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
            error_text = response.text[:200]
            logger.error(f"HTTP错误 {response.status_code}: {error_text}")
            return ChatResponse(
                success=False,
                error=f"Request failed with status {response.status_code}",
                data={"details": error_text}
            )
            
    except requests.Timeout:
        logger.error("请求超时")
        return ChatResponse(success=False, error="Request timeout")
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        return ChatResponse(success=False, error=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
