# proxy.py
import sys
import json
import requests

def send_response(request_id, result):
    """Send a JSON-RPC response to stdout."""
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }
    print(json.dumps(response), flush=True)

def send_error(request_id, code, message):
    """Send a JSON-RPC error to stdout."""
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message}
    }
    print(json.dumps(response), flush=True)

def main():
    print("Proxy started", file=sys.stderr, flush=True)
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            continue
        
        try:
            request = json.loads(line)
            method = request.get("method")
            request_id = request.get("id")  # May be None for notifications
            params = request.get("params", {})

            # Handle notifications (no response needed)
            if method == "notifications/initialized":
                print(f"Received initialized notification", file=sys.stderr, flush=True)
                continue  # No response required for notifications

            # Handle initialize request
            if method == "initialize":
                send_response(request_id, {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "RandomUserProxy", "version": "1.0.0"},
                    "capabilities": {"tools": {}}
                })

            # Handle tools/list request
            elif method == "tools/list":
                response = requests.get("http://localhost:8000/mcp/tools")
                response.raise_for_status()
                tools = response.json()["tools"]
                send_response(request_id, {"tools": tools})

            # Handle tools/call request
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                response = requests.post(
                    "http://localhost:8000/mcp/call_tool",
                    json={"name": tool_name, "arguments": tool_args}
                )
                response.raise_for_status()
                result = response.json()["content"]
                send_response(request_id, {"content": result})

            # Handle unsupported methods with empty responses
            elif method == "resources/list":
                send_response(request_id, {"resources": []})
            elif method == "prompts/list":
                send_response(request_id, {"prompts": []})

            else:
                send_error(request_id, -32601, f"Method not found: {method}")

        except json.JSONDecodeError:
            print("Error: Invalid JSON input", file=sys.stderr, flush=True)
        except requests.RequestException as e:
            send_error(request_id, -32000, f"Server error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}", file=sys.stderr, flush=True)
            if request_id is not None:
                send_error(request_id, -32000, f"Internal server error: {str(e)}")

if __name__ == "__main__":
    main()