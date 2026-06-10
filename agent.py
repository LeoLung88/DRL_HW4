import pandas as pd
import io
import sys
import os
import mimetypes

# 修正 Windows 上載入 google.generativeai 會因為掃描註冊表而卡住的問題
if sys.platform == 'win32':
    mimetypes.MimeTypes.read_windows_registry = lambda self, *args, **kwargs: None

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_data_schema(file_path: str) -> str:
    """Reads a CSV file and returns its column names, data types, and a few sample rows.
    
    Args:
        file_path: The path to the CSV file.
    """
    try:
        df = pd.read_csv(file_path)
        buffer = io.StringIO()
        buffer.write(f"Schema for {file_path}:\n")
        buffer.write(f"Columns and Data Types:\n{df.dtypes}\n\n")
        buffer.write(f"First 3 rows:\n{df.head(3).to_string()}\n")
        return buffer.getvalue()
    except Exception as e:
        return f"Error reading schema: {str(e)}"

def execute_python_code(code: str) -> str:
    """Executes Python code in a local sandbox environment. Useful for data analysis using pandas and matplotlib.
    Always print out the results you want to see using python's print() function.
    If you want to save a chart, save it to the './charts/' directory and make sure the directory exists.
    DO NOT use plt.show().
    
    Args:
        code: The Python code to execute.
    """
    if not os.path.exists('charts'):
        os.makedirs('charts')
        
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    try:
        # Provide local environment
        local_vars = {'pd': pd, 'os': os}
        exec(code, globals(), local_vars)
        sys.stdout = old_stdout
        output = redirected_output.getvalue()
        return output if output else "Code executed successfully with no stdout."
    except Exception as e:
        sys.stdout = old_stdout
        return f"Error executing code: {str(e)}"

class DataAnalysisAgent:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[get_data_schema, execute_python_code],
            system_instruction=(
                "You are a Data Analysis Agent. You can analyze data by writing Python code. "
                "Always use get_data_schema first to understand the data before writing code. "
                "Use pandas to process data. Always print the final results so you can read them. "
                "If asked to plot charts, use matplotlib, create the './charts/' directory if needed, "
                "and save the figure to './charts/'. DO NOT use plt.show() as there is no display. "
                "After the tool execution, provide a clear, user-friendly summary of the findings in Traditional Chinese (繁體中文)."
            )
        )
        # enable_automatic_function_calling=True makes the library automatically run the tool and send back the results
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)
        
    def query(self, user_message: str) -> str:
        try:
            response = self.chat.send_message(user_message)
            return response.text
        except Exception as e:
            return f"Agent Error: {str(e)}"
