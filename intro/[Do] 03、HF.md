<div align="center">

# 3️⃣ 以 Render 為例的部署步驟（最簡單的方式）

</div>

## 🟢 **如何遷移到 Hugging Face Spaces：**

這個過程同樣非常簡單，甚至比 Render 還要直觀一些。

1.  **註冊 Hugging Face 帳號：** 前往 [huggingface.co](https://huggingface.co/) 註冊。
2.  創建一個新的 Space：套件選 **Docker** 選擇 **`Blank`** (空白模板)。
3.  創建 Space。
4.  現在你有一個完全空白的倉庫，點擊 `Add file` -> `Upload files`。
5.  **上傳三個檔案：**
    *   `main.py` (我們的 FastAPI 程式碼)
    *   `requirements.txt`
    *   一個名為 **`Dockerfile`** 的新檔案。
        ```Dockerfile
        # 使用官方 Python 映像
        FROM python:3.11-slim
    
        # 將工作目錄設定為 /app
        WORKDIR /app
    
        # 複製依賴文件
        COPY requirements.txt .
    
        # 安裝依賴
        RUN pip install --no-cache-dir -r requirements.txt
    
        # 複製所有程式碼到工作目錄
        COPY . .
    
        # 暴露端口 (Hugging Face 會自動處理端口映射)
        EXPOSE 7860
    
        # 啟動命令
        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
        ```

---

# ??? Gemini-2.5-pro 還會說到一半轉彎？！
你說得對！非常抱歉，我的記憶出現了一點偏差，並且混淆了兩個相似的名稱。你需要的不是 "Fast AI"，而是 **"FastAPI"**。

*   **FastAPI:** 是一個用來構建 API 的 Python 網頁框架，這是**我們正在使用的**。
*   **fast.ai:** 是一個深度學習函式庫和教育平台。

我猜測你在模板列表中尋找 "Fast AI" 所以沒有找到。請尋找 **"FastAPI"**。

### 修正後的 Hugging Face Spaces 創建步驟

讓我們重新走一遍流程，這次使用正確的名稱。

1.  **登入 Hugging Face** 並點擊 `New Space`。
2.  **Owner** 和 **Space name** 照常填寫。
3.  **Space SDK:** 點擊選擇 **`Docker`**。選擇 **`Blank`** (空白模板)。
4.  **尋找 FastAPI 模板：**
    *   在你選擇 `Docker` 之後，下方會出現一個 **`Docker template`** 的選項。
    *   點擊這個下拉菜單，你應該會看到一個包含多個模板的列表。
    *   在這個列表中，找到並選擇 **`FastAPI`**。

    *(這是一張示意圖，展示了選擇 Docker 後，應該能在模板列表中找到 FastAPI)*

1.  **Space SDK:** 選擇 **`Docker`**。
2.  **Docker template:** 
3.  創建 Space。
4.  現在你有一個完全空白的倉庫，點擊 `Add file` -> `Upload files`。
5.  **上傳三個檔案：**
    *   `main.py` (我們的 FastAPI 程式碼)
    *   `requirements.txt`
    *   一個名為 **`Dockerfile`** 的新檔案。

5.  **Space hardware:** 選擇 `CPU basic - FREE`。
6.  點擊 `Create Space`。

### 如果在 Docker 模板裡也找不到 FastAPI 怎麼辦？

Hugging Face 的介面也時常更新，如果 Docker 模板中真的沒有了 FastAPI 選項，我們有 Plan B，同樣非常簡單：

**Plan B：使用 Gradio 模板，然後自己替換**

`Gradio` 是另一個常用於構建 AI Demo 的 Python 函式庫，Hugging Face 對它的支持是最好的。我們可以先用它創建一個 Space，然後把內容換成我們的 FastAPI 程式。

1.  **Space SDK:** 這次選擇 **`Gradio`**。（這個模板肯定有）
2.  創建 Space。
3.  Hugging Face 會為你生成一個包含 `app.py` 和 `requirements.txt` 的項目。
4.  **進入 `Files and versions` 分頁：**
    *   **重命名 `app.py` 為 `main.py`**（或者你也可以直接修改 `app.py`）。
    *   **刪除 `main.py` (原 `app.py`) 中的所有內容**，然後將我們準備好的 **FastAPI 程式碼** 貼上進去。
    *   **修改 `requirements.txt`：**
        *   刪除裡面原有的 `gradio`。
        *   添加我們需要的函式庫：
            ```txt
            fastapi
            uvicorn
            requests
            ```
5.  **創建 `README.md` 的元數據：**
    *   點擊 `README.md` 文件旁邊的編輯按鈕。
    *   在文件的最頂部，通常會有一段被 `---` 包圍的 YAML 元數據。你需要告訴 Hugging Face 你的應用程式類型。修改或添加以下內容：
        ```yaml
        ---
        title: My Grok Proxy
        emoji: 🚀
        colorFrom: blue
        colorTo: green
        sdk: docker  # 告訴 HF 這是一個 Docker 應用
        app_file: main.py # 告訴 HF 主文件是哪個
        app_port: 7860 # Gradio 默認端口，FastAPI 也可使用
        ---
        ```
    *   **修改 `main.py`**：為了匹配上面的端口，我們需要修改 FastAPI 的啟動命令。但等等，在 HF Space 我們不需要自己寫啟動命令！HF 會自動處理。我們只需要確保 HF 知道主文件和端口。

**等等，讓我們用更簡單的方式！**

忘掉 Plan B 的複雜配置。最簡單的方法是：

### 修正後的最佳方案：使用空白 Docker 模板

1.  **Space SDK:** 選擇 **`Docker`**。
2.  **Docker template:** 選擇 **`Blank`** (空白模板)。
3.  創建 Space。
4.  現在你有一個完全空白的倉庫，點擊 `Add file` -> `Upload files`。
5.  **上傳三個檔案：**
    *   `main.py` (我們的 FastAPI 程式碼)
    *   `requirements.txt`
    *   一個名為 **`Dockerfile`** 的新檔案。

6.  **創建 `Dockerfile`：**
    *   在本地創建一個名為 `Dockerfile` (沒有副檔名) 的文字檔案，內容如下：

    ```Dockerfile
    # 使用官方 Python 映像
    FROM python:3.11-slim

    # 將工作目錄設定為 /app
    WORKDIR /app

    # 複製依賴文件
    COPY requirements.txt .

    # 安裝依賴
    RUN pip install --no-cache-dir -r requirements.txt

    # 複製所有程式碼到工作目錄
    COPY . .

    # 暴露端口 (Hugging Face 會自動處理端口映射)
    EXPOSE 7860

    # 啟動命令
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
    ```
7.  將這個 `Dockerfile` 和其他兩個檔案一起上傳到你的 Hugging Face Space。

上傳完畢後，Hugging Face 會自動根據你的 `Dockerfile` 構建並運行你的應用。這是最標準、最可靠的方法。

再次為之前的混淆致歉！請優先嘗試在 Docker 模板中找到 **FastAPI**，如果找不到，就使用 **Blank Docker 模板 + 手動上傳 `Dockerfile`** 的方案。


