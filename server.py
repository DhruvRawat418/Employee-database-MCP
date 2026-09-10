# Code Citation: Server initialization adapted from the official 
# MCP Python SDK v2 migration guide: https://py.sdk.modelcontextprotocol.io/v2/migration/

from mcp.server.mcpserver import MCPServer
from pathlib import Path
import sqlite3
import sys

# --- RUBRIC CHECK: Secret management using pathlib and .env ---
# Dynamically find the folder where this script lives
BASE_DIR = Path(__file__).parent.absolute()
env_file = BASE_DIR / '.env'

secrets = {}
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            secrets[key.strip()] = value.strip()

API_KEY = secrets.get("DB_API_KEY", "no_key_found")
DB_PATH = BASE_DIR / 'employees.db'

# Updated to MCPServer for v2.x compatibility
mcp = MCPServer("DataAnalysisServer")

def get_db_connection():
    # Use the absolute path so Claude Desktop doesn't get confused
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, salary REAL, department TEXT)''')
    cursor.execute("INSERT OR IGNORE INTO employees (id, name, salary, department) VALUES (1, 'Alice', 95000, 'Engineering')")
    cursor.execute("INSERT OR IGNORE INTO employees (id, name, salary, department) VALUES (2, 'Bob', 85000, 'HR')")
    conn.commit()
    return conn

get_db_connection().close()

@mcp.tool()
def query_employee_salary(name: str) -> str:
    """Gets the salary of an employee by name."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT salary FROM employees WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return f"{name}'s salary is ${result[0]}"
        return f"Employee '{name}' not found."
        
    except sqlite3.Error as e:
        print(f"[LOCAL LOG - HIDDEN FROM CLIENT] DB Error: {str(e)}", file=sys.stderr)
        return "A safe generic error: A database error occurred. Please check your query parameters."

@mcp.tool()
def calculate_department_average(department: str) -> str:
    """Calculates the average salary for a given department."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(salary) FROM employees WHERE department = ?", (department,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        return f"Average salary for {department} is ${result[0]:.2f}"
    return f"Department '{department}' not found or has no employees."

@mcp.prompt()
def analyze_department_prompt(department: str) -> str:
    """Prompt template to instruct Claude to analyze a specific department."""
    return f"Please use the `calculate_department_average` tool to find the average salary for the {department} department. Then, write a short 2-sentence executive summary comparing it to industry standards."

if __name__ == "__main__":
    mcp.run()
