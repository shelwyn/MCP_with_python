# RandomUser MCP Server and Chatbot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains a **RandomUser MCP Server** built with FastAPI, a custom chatbot integrating MCP tools with Gemini-2.0-Flash, and a proxy to connect the server to **Claude Desktop**. The project leverages the **Model Context Protocol (MCP)** to extend AI capabilities with tools for generating random user profiles, demonstrating a practical application of MCP in both standalone and integrated environments.

## Overview

The **RandomUser MCP Server** fetches user data (name, country, age, etc.) from `https://randomuser.me/api/` and exposes three tools:
- `get_random_user`: Fetch a single random user profile.
- `get_multiple_users`: Fetch multiple user profiles (1-10).
- `get_user_by_gender`: Fetch a user profile by gender (male/female).

The **Chatbot** uses these tools via HTTP requests or falls back to Gemini-2.0-Flash for general queries. The **Proxy** bridges the HTTP server to Claude Desktop's stdio-based MCP interface, enabling tool usage within Claude.

## Features

- **MCP Server**: HTTP-based server with FastAPI, exposing tools via `/mcp/tools` and `/mcp/call_tool`.
- **Chatbot**: Command-line interface blending MCP tools with Gemini-2.0-Flash responses.
- **Claude Integration**: Proxy script to connect the server to Claude Desktop.
- **Extensible**: Easy to add new tools or modify existing ones.

## Prerequisites

- **Python 3.8+**
- **Claude Desktop** (optional, for MCP integration)
- **Gemini API Key** (for chatbot LLM functionality)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/shelwyn/MCP_with_python.git
   cd MCP_with_python
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment**:
   Create a `.env` file in the root directory:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   Replace `your_gemini_api_key_here` with your actual Gemini API key from Google.

## File Structure

```
randomuser-mcp/
├── mcp_server.py           # HTTP-based MCP server
├── chatbot.py              # Custom chatbot with MCP and Gemini
├── proxy.py                # Stdio-to-HTTP proxy for Claude Desktop
├── .env                    # Environment variables (not tracked)
├── requirements.txt        # Project dependencies
├── claude_desktop_config.json  # Claude Desktop MCP config (example)
└── README.md               # This file
```

## Usage

### 1. Running the MCP Server

Start the HTTP server:

```bash
python mcp_server.py
```

- Runs on http://localhost:8000
- Endpoints: `/mcp/sse`, `/mcp/tools`, `/mcp/call_tool`

### 2. Running the Chatbot

Launch the chatbot:

```bash
python chatbot.py
```

Examples:
```
You: Get me a random user
Bot: Full Name: Mr John Doe
     Country: United States
     Age: 34
     ...

You: Tell me about the sun
Bot: The Sun is a star at the center of our solar system...

You: exit
```

### 3. Integrating with Claude Desktop

1. **Start the MCP Server**:
   ```bash
   python mcp_server.py
   ```

2. **Configure Claude**:
   Edit `claude_desktop_config.json` (e.g., `C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "randomuser_proxy": {
         "command": "python",
         "args": ["C:/path/to/proxy.py"]
       }
     }
   }
   ```
   Update the path to `proxy.py`.

3. **Restart Claude Desktop**:
   - Close and reopen Claude Desktop.
   - Look for the hammer icon (🔨) in the input box.
   - Test with: "Use get_random_user" or "Call get_multiple_users with count 3".

## Requirements

```
requests==2.31.0
fastapi==0.103.2
uvicorn==0.23.2
sse-starlette==1.6.5
mcp[cli]==0.1.0
google-generativeai==0.4.0
python-dotenv==1.0.0
```

## How It Works

### MCP Server (`mcp_server.py`)
- **Tools**: Defined in `RandomUserTool` class, fetching data from randomuser.me.
- **FastAPI**: Hosts HTTP endpoints, with MCP logic from `mcp.server.Server`.
- **Endpoints**:
  - `/mcp/tools`: Lists tools in MCP format.
  - `/mcp/call_tool`: Executes tools with POSTed arguments.

### Chatbot (`chatbot.py`)
- **Tool Detection**: Parses input for keywords (e.g., "random user") to call MCP tools via HTTP.
- **LLM Fallback**: Uses Gemini-2.0-Flash for non-tool queries.
- **HTTP Client**: Communicates with http://localhost:8000.

### Proxy (`proxy.py`)
- **Bridge**: Translates Claude's stdio JSON-RPC requests to HTTP calls.
- **Methods**: Handles `initialize`, `tools/list`, `tools/call`, and returns empty responses for `resources/list` and `prompts/list`.
- **Runs as Subprocess**: Launched by Claude Desktop via config.

## Troubleshooting

### No Hammer Icon in Claude:
- Ensure `mcp_server.py` is running before starting Claude.
- Check logs in `C:\Users\<YourUsername>\AppData\Roaming\Claude\Logs`.

### Chatbot Errors:
- Verify `.env` has a valid `GEMINI_API_KEY`.
- Ensure MCP server is running.

### Proxy Issues:
- Confirm the path in `claude_desktop_config.json` is correct.
- Add `print("Debug: ...", file=sys.stderr)` in `proxy.py` for logs.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-tool`).
3. Commit changes (`git commit -m "Add new tool"`).
4. Push to the branch (`git push origin feature/new-tool`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Anthropic**: For Claude Desktop and MCP support.
- **Google**: For Gemini-2.0-Flash API.
- **RandomUser.me**: For the free user data API.

## Contact

For questions or suggestions, open an issue or reach out via GitHub.
