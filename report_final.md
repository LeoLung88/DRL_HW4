# AI Harness 系統設計與分析：資料分析代理 (Data Analysis Agent)

## 摘要 (Abstract)
隨著大型語言模型 (LLM) 的快速發展，AI 系統的設計已從單純的「文字接龍」進化為具備行動能力的「代理 (Agent)」。本報告針對「行銷與銷售數據分析」之應用場景，設計了一套基於 AI Harness 架構的「資料分析代理」。本系統透過整合 LLM、記憶體機制與多種外部工具 (Tools)，使不具備程式開發能力的業務人員也能透過自然語言完成複雜的數據清理、統計運算與圖表生成。本報告將詳細論述該系統的問題定義、架構設計、核心工具、工作流程以及評估方法。

---

## 一、 問題定義與應用背景 (Problem Definition & Background)

### 1.1 傳統數據分析的痛點
在現代企業環境中，數據驅動（Data-driven）的決策已成為核心競爭力。然而，企業內的行銷企劃、產品經理或業務人員雖然具備豐富的領域知識（Domain Knowledge），卻往往缺乏撰寫 SQL 查詢或 Python（如 Pandas、Matplotlib 等資料科學套件）的技術能力。
這導致了一種常見的企業瓶頸：當業務端需要一份「各季度產品銷售趨勢分析」時，必須向資料科學團隊或 IT 部門提出需求，經歷繁瑣的溝通、排程與等待，大幅降低了商業決策的時效性。

### 1.2 AI 代理的應用契機
單純的 ChatGPT 或傳統 LLM 雖然能回答統計學問題，但無法直接接觸企業內部的真實數據，也無法確保其憑空捏造的數據具有正確性（幻覺問題, Hallucination）。
因此，我們需要一個 **AI Harness 系統**——一個能將 LLM 安全地包裹起來，並賦予其存取特定資料庫與執行程式碼權限的編排系統 (Orchestration System)。「資料分析代理」即是在此背景下誕生，它旨在扮演一個 24 小時待命的虛擬資料科學家，將使用者的自然語言轉換為精確的程式碼，並自動回報分析結果。

---

## 二、 AI Harness 系統架構設計 (AI System Architecture)

本系統的 AI Harness 架構嚴格遵循「思考、行動、記憶」的設計典範，確保系統具備邏輯一致性與安全性。系統由三個核心模組構成：

### 2.1 系統大腦：LLM Orchestrator (系統控制器)
*   **模型選擇**：採用具備強大 Function Calling 能力與長文本處理能力的大型語言模型（如 Gemini 1.5 系列）。
*   **職責**：作為系統的大腦，負責意圖識別 (Intent Recognition)、任務拆解 (Task Planning)、決定何時呼叫何種外部工具 (Tool Selection)，以及根據工具回傳的「觀察結果 (Observation)」進行下一步推論。

### 2.2 記憶機制 (Memory Management)
為了維持多輪對話的連貫性與執行複雜任務，系統將記憶區分為：
*   **工作記憶 (Short-term Memory)**：存放當前的對話上下文、任務執行的中間狀態（例如：剛生成的 DataFrame 變數名稱）以及程式碼執行失敗時的 Error Logs，確保 LLM 能進行錯誤修復。
*   **長期記憶 (Long-term Memory)**：存放系統已解析的資料庫綱要 (Data Schemas)、常用的商業邏輯定義（例如：「高價值客戶」的定義）以及使用者的視覺化偏好（如圖表配色）。

### 2.3 執行沙盒與工具層 (Tools & Sandbox Environment)
*   LLM 本身不執行程式，而是透過介面呼叫外部環境。
*   **安全沙盒**：所有 LLM 生成的 Python 程式碼皆在一個受限的本機執行空間 (`exec()` 環境或 Docker 容器) 中運行，並攔截所有標準輸出 (stdout)，防止惡意指令破壞主機系統。

---

## 三、 核心工具設計 (Tools Design)

為了使 LLM 能夠獨立完成從「理解資料」到「產出報告」的完整迴圈，本系統設計了以下 3 個核心工具 (Function Calling API)：

### 1. 資料綱要擷取工具：`get_data_schema(file_path: str)`
*   **設計動機**：LLM 若不知道資料表的真實欄位名稱與型態，生成的程式碼高機率會報錯 (如 `KeyError`)。
*   **功能機制**：接收檔案路徑，使用 Pandas 讀取資料表，並回傳欄位名稱 (Columns)、資料型態 (Data Types) 以及前 3 筆範例資料 (Head)。
*   **使用時機**：在使用者提出分析需求後，LLM 規劃程式碼之前的**第一步**必定呼叫此工具作為 Ground Truth。

### 2. 程式碼執行沙盒工具：`execute_python_code(code: str)`
*   **設計動機**：賦予 LLM 實際運算與製圖的能力。
*   **功能機制**：
    *   接收 LLM 生成的 Python 字串。
    *   在注入了 `pandas`、`matplotlib` 等預設環境變數的命名空間中執行程式碼。
    *   利用 `io.StringIO` 攔截 `sys.stdout`，將程式碼中的 `print()` 結果收集後作為字串回傳給 LLM。
    *   若程式碼執行引發 Exception，則捕捉錯誤訊息 (Traceback) 並回傳。
*   **圖表處理**：系統提示限制 LLM 不可使用 `plt.show()`，必須將圖表儲存至指定的本地 `/charts/` 目錄。

### 3. 分析報告生成工具：`generate_markdown_report(insights: list, chart_paths: list)`
*   **設計動機**：確保最終交付給使用者的內容格式統一、結構清晰，而非零散的對話。
*   **功能機制**：當 LLM 判斷所有數據皆已萃取完畢後，將得到的統計數據洞察 (Insights) 與剛生成的圖表路徑 (Chart Paths) 傳入此工具。此工具會將其排版為一份具有標題、重點列表與嵌入圖表的 Markdown 格式字串，作為最終的系統回覆。

---

## 四、 Workflow 與 Agent 流程說明

本系統採用 **ReAct (Reasoning and Acting)** 框架搭配 **Plan-and-Execute** 邏輯。當使用者輸入一個複雜請求（例如：「分析各產品的總銷售額並畫長條圖」）時，系統的執行流程如下：

1. **規劃階段 (Planning Phase)**
   *   **Thought**：LLM 思考「我需要先知道 `sales.csv` 的欄位結構，才能寫 Pandas 程式碼」。
   *   **Action**：呼叫 `get_data_schema('sales.csv')`。
   *   **Observation**：系統回傳包含 `Product`, `Quantity`, `Unit_Price` 等欄位資訊。
2. **程式編寫與執行階段 (Execution Phase)**
   *   **Thought**：LLM 思考「我有了欄位，現在可以計算總銷售額 `Quantity * Unit_Price`，並將結果分組 (GroupBy)」。
   *   **Action**：呼叫 `execute_python_code()`，傳入 Pandas 處理與 Matplotlib 繪圖的程式碼。
   *   **Observation (Error Recovery)**：假設 LLM 將 `Unit_Price` 誤打成 `UnitPrice`，工具將回傳 `KeyError: 'UnitPrice'`。
   *   **Self-Correction**：LLM 進入**自我修正迴圈**，讀取錯誤訊息後，修正欄位名稱並再次呼叫 `execute_python_code()`，直到工具回傳成功執行的 stdout 與圖表儲存成功訊息。
3. **整合與回報階段 (Synthesis Phase)**
   *   **Thought**：LLM 思考「我已經獲得了各產品的銷售額數據，圖表也儲存完畢，可以開始總結報告」。
   *   **Action**：呼叫 `generate_markdown_report()`，將數據整理為條列式說明。
   *   最終，系統將格式化後的分析報告與圖表呈現給使用者。

---

## 五、 系統評估方法 (Evaluation Methods)

由於 Agent 系統具有高度的隨機性與多步驟特性，傳統的機器學習指標（如 Accuracy, F1-score）並不完全適用。本系統設計了以下四個維度的評估指標，以全面衡量 AI Harness 的可靠性：

### 1. 任務成功率 (Task Success Rate)
*   **定義**：給定一個測試資料集與對應的自然語言問題，系統能夠從頭到尾不崩潰，並成功給出最終解答的比例。
*   **衡量方式**：End-to-end 測試。若系統陷入無限的 Tool calling 迴圈或最終給出「無法處理」的結論，則判定為失敗。此為最核心的業務指標。

### 2. 首次程式碼可執行率 (First-Pass Executability)
*   **定義**：LLM **第一次**呼叫 `execute_python_code` 時，程式碼不拋出語法或邏輯錯誤（Exception）即可成功執行的比例。
*   **衡量方式**：統計 Log 中的 Error 發生次數。此指標用於評估系統提示 (System Prompt) 是否足夠清晰，以及 `get_data_schema` 提供的情境是否足夠準確以防止幻覺。

### 3. 錯誤修復率 (Error Recovery Rate)
*   **定義**：當程式碼執行發生例外錯誤（如 KeyError, SyntaxError）時，Agent 能夠透過分析 Error Log，在後續的 3 次嘗試內成功修正程式碼的機率。
*   **衡量方式**：分析 Agent 的 Reasoning 軌跡，衡量其「自我除錯 (Self-Debugging)」的能力。高修復率代表系統具備極佳的魯棒性 (Robustness)。

### 4. 解答相關性與準確度 (Answer Relevance)
*   **定義**：最終產出的數據洞察是否切中要害，計算結果是否數學上完全正確。
*   **衡量方式**：
    *   *自動化評估*：採用 **LLM-as-a-Judge** 框架，使用更強大的模型（如 GPT-4）來交叉比對標準答案與 Agent 輸出的報告。
    *   *人工評估*：由領域專家對生成的報告進行抽樣評分（1-5分），評估其商業價值的可用性。

## 結論
本專案設計之「資料分析代理」，透過嚴謹的 AI Harness 架構，成功將 LLM 的自然語言理解能力與 Python 強大的運算能力相結合。安全沙盒、Schema 解析機制與自我修復工作流的導入，大幅提升了系統的可用性與容錯率，為非技術人員提供了一個高效的數據決策輔助工具。
