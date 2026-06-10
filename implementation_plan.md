# AI Harness 系統設計架構：資料分析代理 (Data Analysis Agent)

本文件根據作業需求 `homework_requirement.md` 設計，旨在提供一個嚴謹的 AI Harness 架構草案，用於實作「資料分析代理」。

## User Review Required

> [!IMPORTANT]
> 請審閱以下系統架構設計。確認場景設定、工具設計與 Workflow 是否符合您對本次作業的期望。這份設計將作為我們後續產出最終報告（書面報告、資訊圖表、log.md）的基礎。

## Open Questions

> [!WARNING]
> 在確認設計前，有幾個問題需要與您討論：
> 1. **應用場景領域：** 目前我以「行銷/銷售數據分析」作為假想情境。您是否有更偏好的特定領域（例如：金融數據、醫療數據、工廠感測器數據等）？
> 2. **視覺化與資訊圖表：** 作業規定需要一份「資訊圖表 (Infographic)」。您希望我後續使用 Mermaid 語法來生成 Sequence Diagram / Flowchart 讓您放入報告中，還是您打算自己使用其他工具（如 Canva, Figma, Draw.io）來繪製？
> 3. **工具設計調整：** 目前設計了 4 個主要工具（擷取 Schema、執行 Python、執行 SQL、產出報告），您認為這是否足夠滿足您的需求？

---

## 1. AI 應用問題定義與使用情境 (Problem Definition)

*   **目標受眾**：不具備程式開發或 SQL 撰寫能力，但需要從龐大數據中獲取洞察的業務人員、行銷企劃或產品經理。
*   **痛點**：傳統資料分析依賴資料科學家或工程師協助撈取資料與製圖，溝通成本高且耗時。
*   **使用情境**：
    1.  使用者上傳一份包含過去一年銷售紀錄的 CSV 檔案。
    2.  使用者輸入：「請幫我分析各季度的產品銷售趨勢，並找出銷量下滑最嚴重的產品線。」
    3.  **資料分析代理** 自動讀取欄位格式、編寫程式碼清理數據、進行統計計算，最終生成包含折線圖與長條圖的總結報告回傳給使用者。

## 2. AI 系統架構 (AI System Architecture)

架構採分層設計，確保邏輯清晰且易於擴充：

*   **System Controller (LLM Orchestrator)**：
    *   作為大腦，負責意圖識別、任務拆解 (Planning)、工具選擇 (Function Calling) 與結果整合。
*   **Memory (記憶機制)**：
    *   **Short-term Memory**：存放對話上下文、當前任務的執行狀態 (State) 以及程式碼執行過程的 Error logs。
    *   **Long-term Memory**：存放已知的資料表綱要 (Data Schemas)、使用者的偏好設定（例如：習慣的圖表配色或格式）。
*   **Tools Layer (工具層)**：
    *   LLM 透過 Function Calling 呼叫的外部環境與函式庫（詳見第 3 節）。
*   **Environment (沙盒環境)**：
    *   安全的 Python REPL 執行環境或唯讀的資料庫連線，確保 AI 生成的程式碼或 SQL 不會造成系統破壞。

## 3. Function Calling / Tool Usage 機制與工具設計

系統採用 **ReAct (Reasoning and Acting)** 結合 Function Calling 的機制。LLM 會先輸出思考過程 (Thought)，決定要呼叫哪個工具，並自動生成 JSON 格式的參數，系統執行後將結果回傳給 LLM 進行下一步判斷。

**至少 3 個核心工具設計：**

1.  `get_data_schema(source_name: str)`
    *   **用途**：當使用者提及某份資料時，LLM 須先呼叫此工具取得該資料的欄位名稱、資料型態 (Data Types) 與前 5 筆範例資料。
    *   **原因**：避免 LLM 產生幻覺 (Hallucination) 寫出不存在的欄位。
2.  `execute_python_code(code: str)`
    *   **用途**：將 LLM 生成的 Python 程式碼 (Pandas, Matplotlib 等) 傳入安全的沙盒環境中執行，用於資料清洗、轉換、統計運算及圖表生成。
    *   **回傳**：執行結果的 stdout、圖表檔案路徑，或 Exception Error Message（若出錯可讓 LLM 自動 debug）。
3.  `execute_sql_query(query: str)`
    *   **用途**：針對結構化關聯式資料庫，執行 SQL SELECT 語法以高效撈取特定維度或聚合後的數據。
4.  `generate_markdown_report(insights: list, chart_paths: list)`
    *   **用途**：當分析完成後，LLM 將整理好的洞察文字與圖表路徑傳入此工具，自動排版成結構化的分析報告回傳給使用者。

## 4. Agent Workflow (多步驟任務執行流程)

採用 **Plan-and-Execute** 流程，分為以下幾個階段：

1.  **Planning Phase (任務拆解)**：
    *   LLM 解析使用者請求。
    *   呼叫 `get_data_schema` 了解資料結構。
    *   制定分析步驟（例如：1. 篩選異常值 -> 2. 按季度 GroupBy -> 3. 繪製折線圖）。
2.  **Execution Phase (循環執行與除錯)**：
    *   LLM 呼叫 `execute_sql_query` 或 `execute_python_code` 執行步驟。
    *   *Self-Correction 機制*：若工具回傳 Error，LLM 會分析 Error Message 並重新呼叫工具修正程式碼，直到成功為止。
3.  **Synthesis Phase (結果整合)**：
    *   LLM 綜合所有的執行結果與圖表，萃取商業洞察。
    *   呼叫 `generate_markdown_report` 產出最終回覆。

## 5. 評估方法 (Evaluation)

為了衡量此「資料分析代理」系統的效能，我們設計以下評估指標：

*   **Task Success Rate (任務成功率)**：系統是否能不發生中斷、成功產出包含解答的報告。（客觀指標）
*   **Code Executability (程式碼可執行率)**：LLM 第一次生成的程式碼/SQL 成功執行的比例。比例越高代表 System Prompt 與 Schema 提供得越精準。
*   **Error Recovery Rate (錯誤修復率)**：當程式碼出錯時，Agent 能夠透過讀取 error log 自動修復並成功執行的機率。
*   **Answer Relevance (回答相關性)**：產出的洞察與圖表是否準確回答了使用者的原始問題。（可透過人工評估或 LLM-as-a-Judge 進行評分）

## 6. AI Orchestration (流程控制與決策方式)

*   **State Machine 架構**：系統流程不只是單純的 prompt in/out，而是以狀態機 (如 LangGraph) 控制。包含節點：`User_Input` -> `Planner` -> `Worker_Agent` (具備 Tool 權限) -> `Reviewer` -> `Final_Output`。
*   **Context Window Management**：為避免長對話導致失憶，Orchestrator 會在每次分析結束後，主動總結對話 (Summarization) 並更新 Long-term Memory。
