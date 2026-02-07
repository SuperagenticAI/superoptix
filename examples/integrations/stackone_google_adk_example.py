"""
Example: StackOne + Google Vertex AI Integration via SuperOptiX Bridge
======================================================================

This example shows how to use StackOne tools with Google's Generative AI SDK
(Gemini models) using the SuperOptiX bridge.
"""

import os
import json
from dotenv import load_dotenv

try:
    from stackone_ai import StackOneToolSet
    from superoptix.adapters import StackOneBridge
    # Note: Requires google-generativeai package
    import google.generativeai as genai
except ImportError as e:
    print(f"Error: {e}")
    print("Please install stackone-ai, google-generativeai, and superoptix.")
    exit(1)

load_dotenv()

def main():
    print("🚀 Initializing StackOne + Google Vertex AI Integration...")

    # 1. Initialize StackOne Toolset
    toolset = StackOneToolSet()

    # 2. Fetch specific tools
    account_id = os.getenv("STACKONE_ACCOUNT_ID", "test_account")
    tools = toolset.fetch_tools(
        include_tools=["hris_get_employee"],
        account_ids=[account_id]
    )

    # 3. Use SuperOptiX Bridge to convert to Google Function Declarations
    bridge = StackOneBridge(tools)
    google_tools = bridge.to_google_adk()
    
    print(f"✅ Converted {len(google_tools)} StackOne tools to Google format.")
    print("   Sample Function Declaration:")
    print(json.dumps(google_tools[0], indent=2))

    # 4. Initialize Gemini Model with Tools
    # Note: This requires GOOGLE_API_KEY
    if os.getenv("GOOGLE_API_KEY"):
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[google_tools] # Pass the list of function declarations
        )
        
        print("\n🤖 Gemini Model Initialized with StackOne Tools")
        
        # 5. Simulate a chat (Using automatic function calling mode)
        chat = model.start_chat(enable_automatic_function_calling=True)
        
        # In a real run, you would execute:
        # response = chat.send_message("Who is employee 123?")
        # print(response.text)
        
    else:
        print("\n⚠️ GOOGLE_API_KEY not found. Skipping model initialization.")

if __name__ == "__main__":
    main()
