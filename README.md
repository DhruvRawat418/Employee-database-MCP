# MCP Data Analysis Server

A local Model Context Protocol (MCP) server for querying an employee database.

## Setup Instructions
1. Clone this repository.
2. Create a virtual environment using `uv`: `uv venv`
3. Activate the environment: `source .venv/bin/activate`
4. Install dependencies: `uv pip install -r requirements.txt`
5. Create a `.env` file in the root directory and add: `DB_API_KEY=your_key_here`
6. Run the server: `python server.py`

## Best Practices Implemented
* **Input Sanitization:** Uses parameterized SQLite queries (`?`) to prevent SQL injection attacks.
* **Error Disclosure Prevention:** Catches `sqlite3.Error` and routes tracebacks to `sys.stderr` while returning a generic, safe string to the client.

## Citations
* MCP Server Initialization: Adapted from the [Official MCP Python SDK v2 Migration Guide](https://py.sdk.modelcontextprotocol.io/v2/migration/).
