# AI Harness 系統設計與分析：資料分析代理 (Data Analysis Agent)

## 一、 問題定義與應用背景
在現代企業環境中，數據驅動（Data-driven）的決策已成為核心競爭力。然而，企業內的行銷企劃、產品經理或業務人員往往具備豐富的領域知識（Domain Knowledge），卻缺乏撰寫 SQL 或 Python（Pandas、Matplotlib 等）的技術能力。這導致他們在進行「行銷/銷售數據分析」時，必須高度依賴資料科學家或工程師協助撈取資料與繪製圖表，不僅溝通成本高昂，也大幅降低了決策效率。

為了打破此技術壁壘，本專案設計了一套**「資料分析代理 (Data Analysis Agent)」**。
該代理作為一個 AI Harness 系統，能夠接收使用者自然語言的分析需求（例如：「請幫我分析各季度的產品銷售趨勢，並找出銷量下滑最嚴重的產品線」），自主在後台解析資料結構、撰寫程式碼進行資料清理與統計計算，並最終產出視覺化圖表與洞察報告。這不僅提升了數據分析的效率，也賦能非技術人員獨立獲取數據價值的能力。

## 二、 AI Harness 系統設計
本系統架構基於 LLM 結合外部工具 (Tools) 與記憶體 (Memory) 設計，旨在實現高度自主化的分析工作流：

1. **System Controller (LLM Orchestrator)**：
   * 系統的大腦（例如使用 GPT-4 或 Gemini 1.5 Pro）。
   * 負責理解使用者的自然語言意圖、進行任務拆解（Task Planning）、決定呼叫何種外部工具（Function Calling），以及根據工具回傳的結果進行下一步決策。
2. **Memory (記憶機制)**：
   * **Short-term Memory (工作記憶)**：存放當前對話上下文、任務執行狀態（State）以及程式碼執行的錯誤日誌（Error Logs），確保 AI 能進行自我修正（Self-Correction）。
   * **Long-term Memory (長期記憶)**：存放已解析的資料庫綱要（Data Schemas）與使用者的偏好設定（如特定的商業邏輯定義或圖表配色習慣）。
3. **Tools & Environment (工具與執行環境)**：
   * 提供獨立且受沙盒保護的 Python REPL 環境與資料庫讀取權限。LLM 無法直接破壞系統，必須透過設計好的 Function Call 來與數據環境互動。

## 三、 Tools 設計（核心工具 API）
為了使 LLM 能夠獨立完成資料分析，系統實作了以下 4 個核心工具：

1. **`get_data_schema(source_name: str)`**
   * **功能**：取得指定資料表或 CSV 檔案的 Schema（包含欄位名稱、資料型態，以及前 5 筆範例資料）。
   * **設計目的**：LLM 雖然具備寫程式的能力，但若不知資料長相容易產生「幻覺 (Hallucination)」而呼叫不存在的欄位。此工具在生成任何查詢代碼前會優先被呼叫以提供 Ground Truth。

2. **`execute_sql_query(query: str)`**
   * **功能**：執行 SQL SELECT 語句。
   * **設計目的**：針對結構化關聯式資料庫，讓 LLM 能夠透過 SQL 高效過濾、分組與聚合巨量數據，減輕後續記憶體與 Python 運算的負擔。工具會回傳查詢結果或資料庫的 Error Message。

3. **`execute_python_code(code: str)`**
   * **功能**：在安全的沙盒環境中執行 Python 程式碼，支援 Pandas, Matplotlib 等數據處理套件。
   * **設計目的**：執行進階的統計分析、特徵轉換以及圖表生成（如折線圖、長條圖）。工具會回傳標準輸出 (stdout)、生成的圖表檔案路徑，或 Python 的 Exception traceback 讓 LLM 自動除錯。

4. **`generate_markdown_report(insights: list, chart_paths: list)`**
   * **功能**：將 LLM 整理出的數據洞察與生成的圖表路徑整合。
   * **設計目的**：格式化輸出結果，自動排版成結構化的 Markdown 分析報告回傳給使用者。

## 四、 Workflow / Agent 流程說明
本系統採用 **ReAct (Reasoning and Acting)** 與 **Plan-and-Execute** 架構進行多步驟任務執行：

1. **規劃階段 (Planning Phase)**：
   使用者上傳檔案或提出問題後，LLM 首先呼叫 `get_data_schema` 理解資料結構，並制定「分析計畫」（例如：先篩選異常值 $\to$ 按季度 GroupBy $\to$ 繪製圖表）。
2. **執行階段 (Execution & Reasoning Phase)**：
   * LLM 開始依照計畫執行，透過 Function Calling 呼叫 `execute_sql_query` 撈取資料，或 `execute_python_code` 進行運算製圖。
   * **錯誤修正循環 (Error Recovery)**：若工具回傳 Error，LLM 會進入 Reasoning 模式，分析 Error Message 並重新撰寫修正後的程式碼/SQL，直到成功執行。
3. **總結階段 (Synthesis Phase)**：
   所有資料與圖表產生完畢後，LLM 總結所有執行結果，萃取商業洞察，並呼叫 `generate_markdown_report` 產出最終回覆。

## 五、 Evaluation 方法（系統效果評估）
為了確保「資料分析代理」的可靠性，系統採用以下指標進行綜合評估：

1. **任務成功率 (Task Success Rate)**：
   衡量系統是否能從頭到尾不發生嚴重中斷（Timeout 或無限錯誤迴圈），成功產出包含解答的報告。（客觀指標）
2. **首次程式碼執行成功率 (First-Pass Executability)**：
   LLM 第一次生成的 SQL 或 Python 程式碼即可成功執行的比例。此指標用於評估 System Prompt 與 `get_data_schema` 提供的 Context 是否足夠精準。
3. **錯誤修復率 (Error Recovery Rate)**：
   當程式碼發生例外錯誤時，Agent 能否透過閱讀 Error Log 自動修改程式碼並在後續嘗試中成功的機率。衡量 Agent 的 Debugging 邏輯能力。
4. **回答準確性與相關性 (Answer Relevance)**：
   產出的洞察報告與圖表是否切中要害，解決了使用者的原始商業問題。這可透過人工領域專家評估（Human Evaluation）或採用 LLM-as-a-Judge 框架進行評分。
