# AI 輔助設計與開發過程紀錄 (log.md)

本文件紀錄了在設計「資料分析代理 (Data Analysis Agent)」過程中的 AI 互動、系統設計迭代、以及相關的架構決策。

## 1. 互動紀錄與需求釐清 (Prompt / Chat History Summary)

* **User Prompt 1**: 
  > 「閱讀資料夾中的 `homework_requirement.md`，輔助我完成這次的作業。 以應用場景: "資料分析代理" 為此專案的核心主題，先不需要實作，而是按照作業需求完整的設計一份嚴謹"AI Harness 系統設計架構"。 若有任何不明白的或是需要額外討論的，請隨時提出。」
* **AI 回覆與設計提議 (Iteration 1)**:
  * 讀取並分析作業需求（需包含架構、工具、工作流、評估方法等）。
  * 提出初步的 **Implementation Plan**（設計草案），設定領域為「行銷/銷售數據分析」，並設計了 4 個核心工具（`get_data_schema`, `execute_python_code`, `execute_sql_query`, `generate_markdown_report`）。
  * 提出 **Open Questions**，向使用者確認預設的領域是否可以接受，以及資訊圖表是否希望透過 Mermaid 語法產生。
* **User Prompt 2**:
  > 「就採用預設的領域 : "行銷/銷售數據分析"，幫我用Mermaid製作一份，其他沒有太大問題，現在開始幫我生成書面報告。 生成的過程中，仍需參考`homework_requirement.md` 確保內容有滿足需求。」

## 2. 系統設計迭代過程與決策 (Design Decisions)

在設計 AI Harness 系統架構時，做出了以下關鍵決策：

1. **核心領域設定：行銷/銷售數據分析**
   * *決策原因*：此領域的數據通常具備明確的欄位（如：日期、商品名稱、銷量、營收），且非技術人員對此類數據的洞察需求極高，是最能體現「資料分析代理」價值的應用場景。

2. **工具設計（Tooling）的必要性劃分**
   * *初步設計*：原本考慮讓 LLM 單純寫 Python 程式碼來完成所有事。
   * *迭代決策*：為了提升穩定性與降低 Hallucination（幻覺），決定拆分出 `get_data_schema` 工具。因為讓 LLM 在寫 SQL 或 Python 之前先「看」過資料長相，能大幅提升首次執行的成功率 (First-Pass Executability)。

3. **記憶機制（Memory）的拆解**
   * *決策原因*：若將所有資訊塞在 prompt 裡，Context Window 容易爆滿且成本過高。因此將 Memory 拆分為 Short-term（儲存當前對話與執行 Error Log）與 Long-term（儲存 Schema 與使用者偏好）。

4. **錯誤修正機制 (Error Recovery)**
   * *決策原因*：程式碼執行極易遇到 Syntax Error 或 KeyError，因此在 Workflow 的 Execution Phase 加入了「Self-Correction」迴圈。當 Sandbox 回傳 Exception 時，強制 LLM 分析錯誤並重新呼叫工具。

## 3. 問題分析與修正過程 (Problem Analysis & Refinement)

* **挑戰**：如何視覺化表現複雜的 AI 工作流？
  * *解決方案*：在製作資訊圖表 (Infographic) 時，決定採用三種不同層次的圖表：
    1. **架構圖 (Graph)**：宏觀展示 LLM、Memory 與 Tools 的關係。
    2. **狀態圖 (State Diagram)**：呈現 Plan-and-Execute 的不同階段轉換。
    3. **循序圖 (Sequence Diagram)**：微觀展示一次問答中，LLM 如何逐步呼叫 Tool 並處理 Error。
  * 透過 Mermaid 語法實作這三張圖表，確保能放入 markdown 中呈現。

* **挑戰**：作業要求確保系統的「可解釋性」。
  * *解決方案*：在架構中加入 `generate_markdown_report` 工具，強迫 AI 把它的統計結論與產出的圖表作最終的統整與輸出，這不僅使結果易於閱讀，也保留了它推理的邏輯軌跡。
