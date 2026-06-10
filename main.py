import os
from agent import DataAnalysisAgent
from dotenv import load_dotenv

def main():
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in .env file.")
        return
        
    print("初始化資料分析代理 (Data Analysis Agent)...")
    agent = DataAnalysisAgent()
    print("✅ 代理已就緒! (輸入 'exit' 或 'quit' 離開)\n")
    print("💡 提示: 您可以從詢問資料結構開始，例如: '這份資料 sales.csv 有哪些欄位？'")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nUser > ")
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            if not user_input.strip():
                continue
                
            print("Agent is thinking and executing... (請稍候)")
            response = agent.query(user_input)
            print(f"\nAgent > {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
