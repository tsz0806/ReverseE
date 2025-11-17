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

---

<div align="center">

# ✨ Replit 有修改的地方

</div>

我剛剛為了讓這個專案能在 Replit 環境中運行，做了以下修改：

## 🟢 修改的檔案：main.py - 只修改了一個地方：
   
   - 將預設端口從 8000 改為 5000（Replit 的標準 web 端口）
   - 第 438 行：port = int(os.environ.get("PORT", 5000))

## 🟢 新增的檔案：
- .gitignore - 新增 Python 專案的 gitignore 規則
   - 包含 Python、虛擬環境、IDE、日誌等常見的忽略項目
- replit.md - 新增專案文檔
   - 記錄專案概述、技術架構、API 端點、使用方法等資訊
   - 方便日後查看專案結構

## 🟢 其他配置：
- 安裝了 Python 3.11 和所有依賴套件（fastapi、uvicorn、requests 等）
- 設置了工作流程（Workflow）來自動運行 python main.py
- 配置了部署設置，使用 autoscale 模式

<div align="center">

# ✨ Replit2 有修改的地方

</div>

我為了讓這個項目在 Replit 環境中運行，做了以下的修改和設置：

## 🟢 修改的檔案
1. main.py (修改)
   
   - 修改內容：將端口從 7860 改為 5000
   - 位置：檔案最後一行
   - 原因：Replit 環境需要使用 5000 端口來顯示網頁預覽

```python
# 修改前
uvicorn.run(app, host="0.0.0.0", port=7860)

# 修改後
uvicorn.run(app, host="0.0.0.0", port=5000)
```

## 🟢 新建的檔案
2. .gitignore (新建)
   
   - 為 Python 項目添加了標準的忽略規則
   - 包含：__pycache__/, *.pyc, 虛擬環境, IDE 設定檔等


3. replit.md (新建)

   - 項目文檔和架構說明
   - 記錄了 API 端點、功能特性、技術堆疊等信息
   - 用於記錄項目歷史和用戶偏好

## 🟢 其他配置
### 安裝依賴
安裝了 Python 3.11
安裝了所有 requirements.txt 中的套件：

### 工作流程設置
配置了「FastAPI Server」工作流程
命令：python main.py
端口：5000
狀態：✅ 正在運行中

### 部署配置
設定為 autoscale 部署模式
適合無狀態的 API 服務
