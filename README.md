# Oblique - AI-Powered API Tester

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge)
![Gradio](https://img.shields.io/badge/Gradio-Framework-orange?style=for-the-badge)

> An intelligent web application to streamline API testing and validation using AI. Quickly verify API responses, analyze performance, and ensure reliability.

[![Demo Video](https://img.shields.io/badge/Demo-Play%20Recording-brightgreen?style=for-the-badge)](https://github.com/user-attachments/assets/124441a3-3f33-48fa-8c3f-b681c88bffe6)

---

## ✨ Features

- **Intelligent Validation**  
  AI-driven analysis of API responses for correctness, structure, and content.
  
- **Performance & Reliability**  
  Detect latency issues, error patterns, and stability concerns in real time.

- **Structured Reports**  
  Clear, actionable reports with debugging suggestions and AI insights.

- **Multi-API Support**  
  Works seamlessly with REST, GraphQL, and other HTTP-based APIs.

- **Intuitive UI**  
  Clean, user-friendly web interface powered by Gradio.

- **Theme Options**  
  Choose between Light, Dark, or System theme for optimal viewing.

- **Screen Studio (Beta)**  
  Record and enhance your testing sessions for documentation or debugging.

---

## 💡 How It Works

1. **Input**  
   Enter the API URL, HTTP method (GET, POST, etc.), and expected response fields.

2. **Request & Response**  
   The app sends the request and captures the full response (headers, body, status).

3. **AI Analysis**  
   Our AI validates the response against your criteria — checks data types, required fields, formats, and more.

4. **Reporting**  
   Get a comprehensive report including:
   - Status code
   - Response time
   - Field validation results
   - AI-generated suggestions for fixes or improvements

---

## 🎯 Why Use It?

Automate repetitive API testing tasks with intelligent validation. Ideal for:

- Validating response formats (e.g., JSON schema)
- Security checks (e.g., missing headers, exposed data)
- Performance benchmarking
- Regression testing
- Auto-generating test documentation
- Onboarding new developers with smart feedback

Perfect for developers, QA engineers, and DevOps teams.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- `pip` package manager

### Setup & Run

1. **Install Dependencies**

```bash
pip install gradio requests openai python-dotenv
```

2. **Run the App**

```bash
python api_tester.py
```

3. **Access the App**
Open your browser and go to:

```bash
http://127.0.0.1:7860
```

---

### API Usage
Interact programmatically via Python, JavaScript, or cURL.
Check the in-app "API Documentation" tab for full endpoint details.

```code
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
    api_url="https://jsonplaceholder.typicode.com/posts/1",
    method="GET",
    expected_fields="userId, id, title, body",
    api_name="/test_api"
)
print(result)
```

---

### Settings

Customize your experience directly in the web app:

- **Display Theme**: Light / Dark / System
- **Language**: English (more coming soon)
- **Screen Studio**: Enable recording and annotation (Beta)

---

### License

This project is licensed under the MIT License.

---

### 🙏 Acknowledgements

Built with ❤️ using Gradio - the fastest way to demo machine learning apps.
