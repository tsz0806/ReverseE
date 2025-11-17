<div align="center">

# 2️⃣ 如何在開發者工具中找到正確的 API 請求

</div>

## 🟢 步驟 1：清理和準備

1. **清空 Network 記錄**
2. **設置過濾器**
   - 點擊 `Fetch/XHR` 或 `XHR` - 這會過濾出 API 請求

## 🟢 步驟 2：捕捉請求

```markdown
1. 確保 Network 分頁是開啟的
2. 確保紅色錄製按鈕是啟用的（應該是紅色，不是灰色）
3. 現在發送一條消息，例如："你好"
4. 觀察 Network 面板中新出現的請求
```

## 🟢 步驟 3：識別正確的請求

### 看這些特徵：

| 特徵 | 說明 |
|------|------|
| **Method** | 通常是 `POST` |
| **Status** | 應該是 `200` 或 `101`（WebSocket） |
| **Type** | `fetch` 或 `xhr` 或 `websocket` |
| **Size** | 通常不會太小（因為包含回應內容） |
| **Time** | 可能需要幾秒（AI 生成需要時間） |

### 常見的 API 端點名稱模式：
- `/api/chat`
- `/api/completions`
- `/v1/chat/completions`
- `/conversation`
- `/messages`
- `/generate`
- `/stream`

## 🟢 步驟 4：詳細檢查

找到可疑的請求後，點擊它：

### A. 檢查 Headers 分頁
```javascript
// 重點關注這些：
Request URL: https://example.com/api/chat
Request Method: POST
Status Code: 200

// Request Headers 中尋找：
Authorization: Bearer xxxxx...
Content-Type: application/json
Cookie: session=xxxxx...
```

### B. 檢查 Payload/Request 分頁
```json
// 你應該能看到你發送的消息
{
  "message": "你好",
  "conversation_id": "xxx",
  "model": "grok-1"
}
```

### C. 檢查 Response/Preview 分頁
```json
// 應該包含 AI 的回應
{
  "response": "你好！有什麼可以幫助你的嗎？",
  "id": "xxx"
}
```

## 🟢 步驟 5：如果是 WebSocket

如果網站使用 WebSocket（即時通訊）：

1. 在 Filter 中選擇 `WS`
2. 找到狀態碼為 `101` 的請求
3. 點擊它，然後選擇 `Messages` 分頁
4. 你會看到來回的消息流

## 🟢 實用技巧

### 1. 使用搜尋功能
按 `Ctrl+F` 在 Network 面板中搜尋：
- 搜尋你發送的消息內容（如 "你好"）
- 搜尋 "chat" 或 "message"

### 2. 按大小排序
點擊 `Size` 欄位標題，較大的請求通常是 API 回應

### 3. 按時間排序
點擊 `Time` 欄位，耗時較長的通常是 AI 處理請求

## 🟢 範例截圖說明

```
Network 面板結構：
┌─────────────────────────────────────────┐
│ 🔴 ⏸ 🚫  Filter: [All][XHR][JS][CSS]... │
├─────────────────────────────────────────┤
│ Name          Status  Type    Size Time │
│ ─────────────────────────────────────── │
│ chat          200     fetch   2.3KB 3.2s│ ← 這個很可能是
│ analytics     200     fetch   124B  23ms│
│ status        200     xhr     89B   15ms│
└─────────────────────────────────────────┘
```

## 🟢 如果還是找不到

### 嘗試這個方法：
```javascript
// 在 Console 中輸入這個程式碼來攔截所有 fetch 請求
(function() {
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        console.log('Fetch 請求:', args);
        return originalFetch.apply(this, args);
    };
})();
```

### 或攔截 XMLHttpRequest：
```javascript
// 攔截所有 XHR 請求
(function() {
    const open = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function() {
        console.log('XHR 請求:', arguments);
        return open.apply(this, arguments);
    };
})();
```

## 🟢 找到後要記錄的資訊

創建一個文檔記錄：
```yaml
API 端點資訊：
  URL: https://mirror-site.com/api/chat
  Method: POST
  
Headers:
  Authorization: "Bearer sk-xxxxx"
  Content-Type: "application/json"
  Cookie: "session=xxxxx; user_id=xxxxx"
  
Request Body 格式:
  {
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "model": "grok-1",
    "stream": false
  }
  
Response 格式:
  {
    "id": "chatcmpl-xxx",
    "choices": [
      {"message": {"content": "你好！"}}
    ]
  }
```
