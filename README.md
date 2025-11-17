# ReverseE

> 本專案為作業用途，純紀錄，請勿模仿

[![Built with](https://img.shields.io/badge/Built%20with-Stima%20API-blueviolet?logo=robot)](https://api.stima.tech)

## 📊 **資料流程圖**

```
┌─────────────┐
│   Dify      │
│  (使用者輸入)│
└──────┬──────┘
       │ 發送 POST 請求
       │ {"message": "你好"}
       ▼
┌─────────────────────────┐
│  你的 FastAPI 服務       │
│  (Hugging Face Space)   │
│                         │
│  1. 接收請求            │
│  2. 新增 Cookie 等認證  │
│  3. 建構完整請求本體    │
└──────┬──────────────────┘
       │ 發送 POST 請求到 Grok
       │ 包含所有從 F12 取得的資料
       ▼
┌─────────────────────────┐
│  Grok 鏡像網站          │
│  grok.ylsagi.com        │
│                         │
│  1. 驗證 Cookie         │
│  2. 處理請求            │
│  3. 串流式回傳回覆      │
└──────┬──────────────────┘
       │ 串流式回應（逐字發送）
       │ {"result":{"response":{"token":"你"}}}
       │ {"result":{"response":{"token":"好"}}}
       │ {"result":{"response":{"token":"！"}}}
       │ ...
       ▼
┌─────────────────────────┐
│  你的 FastAPI 服務       │
│                         │
│  1. 逐行解析回應        │
│  2. 拼接所有 token      │
│  3. 提取完整回覆        │
└──────┬──────────────────┘
       │ 回傳 JSON
       │ {"success": true, "data": {"response": "你好！"}}
       ▼
┌─────────────┐
│   Dify      │
│  (顯示回覆)  │
└─────────────┘
```
