<div align="center">

# 3️⃣ 以 Replit 為例的部署步驟（程式碼不變）

</div>

## 🟢 準備你的程式碼：

1. 將你的 FastAPI 程式碼保存為 `main.py`。
2. 設定 `requirements.txt`
3. 設定 `Dockerfile`

## 🟢 **推送到 GitHub：**
    *   註冊一個 GitHub 帳號。
    *   創建一個新的倉庫 (Repository)。
    *   將你的 `main.py`、`requirements.txt` 和 `Dockerfile` 這幾個檔案上傳到這個倉庫。

## 🚀 **立即開始：Replit 快速部署**

### 步驟：
1. **訪問** [replit.com](https://replit.com)
2. **註冊/登入**（可用 Google/GitHub）
3. **Import to Replit** 
4. **從 GitHub 導入**：
   > 原本要先將 FastAPI 的檔案移到根目錄，但現在 Replit 的 AI Agent 功能很發達，他會自己讀完 Github 資料夾裡面的所有內容，然後自己部屬（超強！）
   
    ```text
    1. 選擇 "Import from GitHub"
    2. 貼上你的 repo URL：
       https://github.com/[你的用戶名]/ReverseE
    3. 選擇 Branch（通常是 main）
    4. 點擊 Import
    ```

## 🟢 **推送到 GitHub：**
- 好了之後右邊會顯示部屬完的結果
- 確定了之後，點擊網址欄位，就會跳出可以複製、末尾名為`.dev`的網址，這個就是我們要的
- `.dev`的網址只有在 workspace 打開的時候會運行，如果要持久一點的話，需要`.app`的網址，但要 publish 要先付費

<img src="/image/image05.png" width="100%">


