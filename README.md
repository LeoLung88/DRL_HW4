# 資料分析代理 (Data Analysis Agent) - AI Harness MVP

本專案為「AI Harness 系統設計與分析」之實作作業。我們設計並實作了一個具備自主分析數據能力的「資料分析代理 (Data Analysis Agent)」，能夠接收自然語言指令，在後台自動撰寫 Python 程式碼進行數據分析與圖表生成，降低非技術人員進行數據決策的門檻。

## 🎯 專案亮點與核心架構

本系統基於 **AI Harness 架構** 與 **ReAct (Reasoning and Acting)** 工作流進行設計，賦予大型語言模型 (LLM) 存取真實環境數據的權限：

*   **LLM Orchestrator**：採用 Gemini 1.5 Flash，負責意圖識別、任務拆解與邏輯推理。
*   **工具層 (Tools)**：
    *   `get_data_schema`：讓 LLM 在分析前了解資料庫或 CSV 的真實欄位結構，避免幻覺。
    *   `execute_python_code`：本機安全沙盒，允許 LLM 使用 Pandas 與 Matplotlib 執行真正的數據計算與繪圖，並捕捉執行錯誤 (Exception) 以進行自我修復 (Self-Correction)。
*   **多步驟任務流**：支援從「了解資料 -> 處理資料 -> 視覺化繪圖 -> 產出洞察」的端到端自動化流程。

## 📂 作業交付檔案導覽

依照作業需求，相關的設計文件與報告皆存放在本 Repo 中：

*   📄 **[report_final.md](./report_final.md)**：包含問題定義、系統架構、核心工具解析與評估指標的完整書面報告。
*   📊 **[infographic.md](./infographic.md)**：使用 Mermaid 語法繪製的系統架構圖、Agent 工作流狀態圖與 Tool calling 循序圖。
*   📝 **[log.md](./log.md)**：AI 輔助設計與開發過程中的互動紀錄與架構決策日誌。

---

## 🚀 如何在本機執行 MVP

### 1. 環境前置準備 (Prerequisites)
請確保您的系統已安裝 Python 3.8+，並準備好您的 **Gemini API Key**。

### 2. 安裝與設定 (Installation & Setup)

1. **複製專案**
   ```bash
   git clone https://github.com/LeoLung88/DRL_HW4.git
   cd DRL_HW4
   ```

2. **建立並啟動虛擬環境 (建議)**
   * Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   * macOS / Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **安裝相依套件**
   ```bash
   pip install -r requirements.txt
   ```

4. **設定環境變數**
   在專案根目錄建立 `.env` 檔案，並填入您的金鑰：
   ```env
   GEMINI_API_KEY=您的_API_KEY_字串
   ```

### 3. 生成測試資料與執行
本專案內建一個腳本，可為您自動生成 500 筆測試用的行銷銷售數據 (`sales.csv`)。

```bash
# 生成 sales.csv
python generate_data.py

# 啟動終端機代理程式
python main.py
```

### 4. 測試劇本範例 (Example Queries)
啟動 `main.py` 後，您可以嘗試輸入以下自然語言問題：
*   *"這份資料 sales.csv 有哪些欄位？"*
*   *"幫我算出哪個區域 (Region) 的總銷售額最高？"*
*   *"請幫我畫出一張各產品銷量總和的長條圖"* (圖表生成後，請至專案的 `charts/` 目錄中檢視)。

---
> **Disclaimer:** 本專案的 `execute_python_code` 工具採用本機 `exec()` 作為沙盒實作，僅供 MVP 概念驗證與作業展示。若要部署至正式生產環境，應將其隔離至 Docker 容器或更安全的隔離環境中。