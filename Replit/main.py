# ================================

# ================================
# 第二部分：建立 FastAPI 應用程式
# ================================

app = FastAPI(
    title="Grok Mirror API",  # API 名稱
    version="3.3.0"  # 版本號
)

# 新增 CORS 中介軟體
# 作用：允許任何網站呼叫這個 API（Dify 需要這個功能）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源（正式環境應該限制）
    allow_credentials=True,  # 允許發送 Cookie
    allow_methods=["*"],  # 允許所有 HTTP 方法（GET, POST 等）
    allow_headers=["*"],  # 允許所有 HTTP 標頭
)

# ================================
# 第三部分：關鍵設定（從 F12 取得）
# ================================

GROK_BASE_URL = "https://grok.ylsagi.com"  # Grok 鏡像網站的基礎 URL

# ⭐⭐⭐ 重點！這些都是從 F12 開發者工具擷取的 ⭐⭐⭐
HEADERS = {
    "Content-Type": "application/json",  # 標準 HTTP 標頭
    
    # 🔑 來源：F12 → Network → 選擇請求 → Request Headers → Cookie
    # 作用：身分驗證，證明你已經登入
    # 如何取得：
    #   1. 在 Grok 網站發送訊息
    #   2. 按 F12 開啟開發者工具
    #   3. Network 標籤 → 找到 responses 請求
    #   4. Headers 標籤 → Request Headers → 複製 Cookie 那一整行
    "Cookie": 'share_token=aaf6c70a7ba8832ae9b09ac055cd1081947d2d897b3ca2b65d826ceeecbcf653; imgID=67e253bdd0b63c582005f9a7; i18nextLng=en; mp_ea93da913ddb66b6372b89d97b1029ac_mixpanel=%7B%22distinct_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%2C%22%24device_id%22%3A%229c284b9a-2aa5-4b8e-886e-78017fc21d9e%22%2C%22%24initial_referrer%22%3A%22https%3A%2F%2Fylsagi.com%2F%22%2C%22%24initial_referring_domain%22%3A%22ylsagi.com%22%2C%22__mps%22%3A%7B%7D%2C%22__mpso%22%3A%7B%7D%2C%22__mpus%22%3A%7B%7D%2C%22__mpa%22%3A%7B%7D%2C%22__mpu%22%3A%7B%7D%2C%22__mpr%22%3A%5B%5D%2C%22__mpap%22%3A%5B%5D%2C%22%24user_id%22%3A%2200a70e22-fed7-4713-b4c5-9b16ba9c856f%22%7D',
    
    # 🔑 來源：F12 → Request Headers → User-Agent
    # 作用：偽裝成瀏覽器，避免被識別為機器人
    # 如何取得：在 F12 的 Request Headers 中直接複製
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
    
    # 🔑 來源：F12 → Request Headers → Origin 和 Referer
    # 作用：告訴伺服器請求來自哪裡
    "Origin": "https://grok.ylsagi.com",
    "Referer": "https://grok.ylsagi.com/",
}

# ================================
# 第四部分：資料模型定義
# ================================

class ChatRequest(BaseModel):
    """
    定義客戶端（如 Dify）發送給這個 API 的請求格式
    
    範例：
    {
        "message": "你好",
        "model": "grok-3"
    }
    """
    message: str  # 必需：使用者的問題
    model: Optional[str] = "grok-3"  # 可選：使用的模型，預設 grok-3

class ChatResponse(BaseModel):
    """
    定義這個 API 回傳給客戶端的回應格式
    
    成功範例：



