# chatbot.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")  # Updated to gemini-2.0-flash

# MCP client functions
def call_mcp_tool(name, arguments=None):
    if arguments is None:
        arguments = {}
    try:
        response = requests.post("http://localhost:8000/mcp/call_tool", json={"name": name, "arguments": arguments})
        response.raise_for_status()
        return response.json()["content"][0]["text"]
    except requests.RequestException as e:
        return f"Error contacting MCP server: {str(e)}"

def process_tool_request(user_input):
    """Determine if the input requires an MCP tool and execute it."""
    user_input = user_input.lower()
    
    if "random user" in user_input:
        if "multiple" in user_input or "users" in user_input:
            count = 5
            for word in user_input.split():
                if word.isdigit():
                    count = int(word)
            return call_mcp_tool("get_multiple_users", {"count": count})
        elif "male" in user_input:
            return call_mcp_tool("get_user_by_gender", {"gender": "male"})
        elif "female" in user_input:
            return call_mcp_tool("get_user_by_gender", {"gender": "female"})
        else:
            return call_mcp_tool("get_random_user")
    return None

def chatbot_response(user_input):
    """Generate a response using Gemini LLM or the MCP tool."""
    tool_result = process_tool_request(user_input)
    if tool_result is not None:
        return tool_result
    
    try:
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def main():
    print("Welcome to the Chatbot! Type 'exit' to quit.")
    print("Using MCP server at http://localhost:8000 and Gemini-2.0-Flash.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        response = chatbot_response(user_input)
        print(f"Bot: {response}")

if __name__ == "__main__":
    main()