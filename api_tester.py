import json
import os
import gradio as gr
import requests
from dotenv import load_dotenv

# --- Robustly load environment variables ---
# This constructs an absolute path to the .env file, assuming it's in the same
# directory as the script. This is more reliable than a simple load_dotenv().
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Get the API key from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def parse_json_input(text: str) -> dict:
    """
    Helper function to safely parse JSON input from a Gradio textbox.
    Returns an empty dictionary if the input is empty or invalid.
    """
    if not text or not text.strip():
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON input provided: {text}")
        return {}


def test_api(api_url: str, method: str, headers_text: str, payload_text: str, expected_fields: str):
    """
    Tests an API endpoint, validates the response using the OpenRouter API, and returns a formatted report.

    Args:
        api_url: The URL of the API endpoint to test.
        method: The HTTP method ('GET' or 'POST').
        headers_text: A string containing headers in JSON format.
        payload_text: A string containing the request body in JSON format.
        expected_fields: A comma-separated string of fields expected in the response.

    Returns:
        A tuple containing the API summary, the AI-generated markdown report, and the raw JSON response.
    """
    # --- 1. Pre-computation Checks ---
    if not OPENROUTER_API_KEY:
        error_msg = "## ❌ Error\n\n`OPENROUTER_API_KEY` not found. Please ensure it is set in your `.env` file and the script can access it."
        return error_msg, None, None
    if not api_url:
        error_msg = "## ❌ Error\n\nPlease enter the API Endpoint URL you want to test."
        return error_msg, None, None

    try:
        # --- 2. Prepare and Send the User's API Request ---
        headers = parse_json_input(headers_text)
        payload = parse_json_input(payload_text)

        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        if method.upper() == "GET":
            response = requests.get(api_url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        else:
            return f"## ❌ Error\n\nUnsupported method: {method}. Please use GET or POST.", None, None

        response_time = response.elapsed.total_seconds() * 1000

        try:
            response_data = response.json()
            response_json_str = json.dumps(response_data, indent=2)
        except json.JSONDecodeError:
            response_data = None
            response_json_str = response.text
            ai_validation_report = "Skipping AI validation because the response was not valid JSON."

        # --- 3. Perform AI-Based Validation (if response was JSON) ---
        if response_data:
            # Truncate the response if it's too large to avoid token limit errors
            response_for_prompt_str = json.dumps(response_data, indent=2)
            truncation_note = ""
            if len(response_for_prompt_str) > 4000:  # Approx 1000 tokens
                response_for_prompt_str = response_for_prompt_str[:4000] + "\n..."
                truncation_note = "\n\n**Note:** The API response was too large and has been truncated for analysis."

            prompt = f"""
            You are an expert API Testing Assistant. Your task is to analyze and validate a JSON response from an API call based on a list of expected fields.
            {truncation_note}

            **API Response to Analyze:**
            ```json
            {response_for_prompt_str}
            ```

            **Validation Criteria:**
            The response should contain the following fields: `{expected_fields}`.

            **Your Analysis:**
            Please provide your analysis in Markdown format with the following structure:
            1.  **Summary:** A brief, one-sentence conclusion about whether the validation was successful.
            2.  **Fields Check:**
                * **✅ Present Fields:** List the expected fields that were found in the response.
                * **❌ Missing Fields:** List the expected fields that were NOT found in the response. If all fields are present, state "None".
            3.  **Suggestions:** (Optional) Provide any other relevant observations or suggestions about the response structure or content.
            """

            ai_payload = {
                "model": "x-ai/grok-4",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024  # Add a safeguard for response length
            }
            ai_headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            # Call the OpenRouter API
            ai_response = requests.post(
                OPENROUTER_API_URL,
                json=ai_payload,
                headers=ai_headers,
                timeout=20
            )

            if ai_response.status_code == 200:
                ai_result = ai_response.json()
                try:
                    ai_validation_report = ai_result['choices'][0]['message']['content']
                except (KeyError, IndexError):
                    ai_validation_report = "AI validation failed: Could not parse the response from the OpenRouter API."
            elif ai_response.status_code == 402:
                ai_validation_report = (
                    "**AI Validation Failed: Insufficient Credits (Error 402)**\n\n"
                    "The request to the AI model failed because you've exceeded your free credit limit on OpenRouter. "
                    "This usually happens when the API response being analyzed is very large. "
                    "The app has attempted to shorten the response, but it may still be too large for the free tier. "
                    "Please check your OpenRouter account or try with a smaller API response."
                )
            else:
                ai_validation_report = f"AI validation failed. Status: {ai_response.status_code}\nResponse: {ai_response.text}"
        else:
            ai_validation_report = "AI validation was not performed because the API response was not valid JSON."

        # --- 4. Construct Final Output ---
        summary_report = f"""
        ### ✅ API Test Summary
        * **Status Code:** `{response.status_code}`
        * **Response Time:** `{response_time:.2f} ms`
        """
        return summary_report, ai_validation_report, response_json_str

    except requests.exceptions.RequestException as e:
        return f"## ❌ API Request Error\n\nCould not connect to the API endpoint.\n**Details:** {str(e)}", None, None
    except Exception as e:
        return f"## ❌ An Unexpected Error Occurred\n\n**Details:** {str(e)}", None, None


# --- Create the Gradio Interface using Blocks for better layout ---
with gr.Blocks(theme=gr.themes.Soft(primary_hue="sky"), title="📤Oblique: AI-Powered API Tester") as interface:
    gr.Markdown("""
    # 📤Oblique: AI-Powered API Tester
    Test any API endpoint and get intelligent validation powered by AI. This tool helps developers and QA engineers verify API responses quickly.
    """)

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 🔧 Configuration")

            api_url = gr.Textbox(
                label="🌐 API Endpoint URL",
                placeholder="e.g., https://jsonplaceholder.typicode.com/posts/1",
                value="https://jsonplaceholder.typicode.com/posts/1"
            )

            method = gr.Radio(
                ["GET", "POST"],
                label="HTTP Method",
                value="GET"
            )

            expected_fields = gr.Textbox(
                label="🎯 Expected Response Fields",
                placeholder="e.g., userId, id, title, body",
                value="userId, id, title, body",
                info="Comma-separated list of fields to check for in the response."
            )

            with gr.Accordion("Advanced: Headers & Body", open=False):
                headers = gr.Code(
                    label="📋 Headers",
                    language="json",
                    lines=3,
                    value='{\n  "Content-Type": "application/json"\n}'
                )
                payload = gr.Code(
                    label="📦 Request Body (for POST)",
                    language="json",
                    lines=4,
                    value='{\n  "key": "value"\n}'
                )

            test_btn = gr.Button("🚀 Run Test & AI Validation", variant="primary", size="lg")

        with gr.Column(scale=3):
            gr.Markdown("### 📊 Results")
            output_summary = gr.Markdown(label="✅ API Test Summary")
            output_report = gr.Markdown(label="🤖 AI Validation Report", value="*Your test report will appear here...*")
            output_response = gr.Code(label="Raw API Response", language="json", interactive=False)

    gr.Markdown("---")
    gr.Markdown("### 📝 Quick Examples")
    gr.Examples(
        examples=[
            [
                "https://jsonplaceholder.typicode.com/posts/1",
                "GET",
                '{"Content-Type": "application/json"}',
                '',
                "userId,id,title,body"
            ],
            [
                "https://api.github.com/users/gradio-app",
                "GET",
                '{"Accept": "application/vnd.github.v3+json"}',
                '',
                "login,id,name,followers,public_repos"
            ],
            [
                "https://httpbin.org/post",
                "POST",
                '{"Content-Type": "application/json"}',
                '{"name": "AI Tester", "version": 1.0, "status": "active"}',
                "json,url,headers"
            ],
        ],
        inputs=[api_url, method, headers, payload, expected_fields],
        outputs=[output_summary, output_report, output_response],
        fn=test_api,
        cache_examples=True,
        label="Click an example to run"
    )

    # Link the button to the main function
    test_btn.click(
        fn=test_api,
        inputs=[api_url, method, headers, payload, expected_fields],
        outputs=[output_summary, output_report, output_response],
        api_name="test_api"
    )

# Launch the web app
if __name__ == "__main__":
    # Use os.path.abspath to handle potential issues with __file__ in some environments
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(script_dir, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
    else:
        print("Warning: .env file not found. Make sure it's in the same directory as the script.")

    interface.launch(debug=True)
