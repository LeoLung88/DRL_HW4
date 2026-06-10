# 資料分析代理 (Data Analysis Agent) 資訊圖表

本文件透過視覺化圖表呈現 AI Harness 的系統設計，包含系統架構、工作流程與 Function Calling 呼叫流程。

## 1. 系統架構圖 (System Architecture)
呈現 LLM, Memory, Tools 與執行環境之間的關係與資料流向。

```mermaid
graph TD
    User([User]) -- "Natural Language Query\n(e.g., 分析銷售趨勢)" --> Interface

    subgraph AI Harness System [AI Harness System (System Controller)]
        Interface[Chat Interface]
        LLM{LLM Orchestrator\n(GPT-4 / Gemini)}
        
        subgraph Memory
            STM[(Short-term Memory)\n- Context\n- Error Logs\n- State]
            LTM[(Long-term Memory)\n- Data Schemas\n- User Preferences]
        end
        
        Interface <--> LLM
        LLM <--> STM
        LLM <--> LTM
    end

    subgraph Tools Layer [Tools Layer / Function Calling]
        T_Schema[get_data_schema]
        T_SQL[execute_sql_query]
        T_Python[execute_python_code]
        T_Report[generate_markdown_report]
    end

    subgraph Sandbox Environment [Sandbox / Execution Environment]
        DB[(SQL Database)]
        REPL[Python REPL\n(Pandas, Matplotlib)]
    end

    LLM -- "Selects & Calls" --> T_Schema
    LLM -- "Selects & Calls" --> T_SQL
    LLM -- "Selects & Calls" --> T_Python
    LLM -- "Selects & Calls" --> T_Report

    T_Schema --> DB
    T_SQL --> DB
    T_Python --> REPL
```

## 2. 代理工作流程圖 (Agent Workflow Flowchart)
呈現 Plan-and-Execute 的多步驟任務執行邏輯。

```mermaid
stateDiagram-v2
    [*] --> Input: User Query Uploaded
    
    state "Planning Phase" as Planning {
        Input --> Understand
        Understand --> Plan: get_data_schema()
        Plan --> Execution_Phase: Generated Analysis Plan
    }
    
    state "Execution Phase (ReAct Loop)" as Execution_Phase {
        state "Tool Selection" as TS
        state "Execute Tool (SQL/Python)" as Exec
        state "Evaluate Result" as Eval
        
        TS --> Exec: Function Call
        Exec --> Eval: Return stdout/Error
        Eval --> TS: Error (Self-Correction)
        Eval --> Synthesis_Phase: Success & Complete
    }
    
    state "Synthesis Phase" as Synthesis_Phase {
        state "Data Insight Generation" as Insight
        state "generate_markdown_report()" as GenReport
        
        Insight --> GenReport
    }
    
    GenReport --> Output: Final Report & Charts
    Output --> [*]
```

## 3. Function Calling / Tool Chain 循序圖 (Sequence Diagram)
詳細展示在一次分析請求中，各組件間的呼叫順序與資料傳遞。

```mermaid
sequenceDiagram
    actor User
    participant LLM as LLM Orchestrator
    participant Tool_Schema as get_data_schema()
    participant Tool_Python as execute_python_code()
    participant Tool_Report as generate_markdown_report()

    User->>LLM: 請問第一季銷量最差的產品是？ (附帶 sales.csv)
    
    rect rgb(240, 248, 255)
        Note over LLM,Tool_Schema: 1. 了解資料結構 (Planning)
        LLM->>Tool_Schema: Call get_data_schema('sales.csv')
        Tool_Schema-->>LLM: Return (Columns: Date, Product, Qty, Price)
    end
    
    rect rgb(255, 250, 240)
        Note over LLM,Tool_Python: 2. 執行資料分析 (Execution)
        LLM->>Tool_Python: Call execute_python_code(df.groupby('Product')['Qty'].sum())
        
        alt Execution Error
            Tool_Python-->>LLM: Return KeyError: 'Prodct' (Typo)
            LLM->>Tool_Python: Call execute_python_code(df.groupby('Product')['Qty'].sum()) (Self-corrected)
        end
        
        Tool_Python-->>LLM: Return stdout: Product C has lowest Qty: 15
        
        Note over LLM,Tool_Python: 2.1 產生視覺化圖表
        LLM->>Tool_Python: Call execute_python_code(plot_bar_chart())
        Tool_Python-->>LLM: Return Chart Path: '/charts/bar1.png'
    end
    
    rect rgb(245, 255, 250)
        Note over LLM,Tool_Report: 3. 整合與回報 (Synthesis)
        LLM->>Tool_Report: Call generate_markdown_report(insights, chart_paths)
        Tool_Report-->>LLM: Return Formatted Markdown
    end
    
    LLM->>User: 回傳分析報告與圖表
```
