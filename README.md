# 🤖 Omni-LLM-Proxy

> **Silent Multi-LLM Browser Proxy** — One unified API endpoint for ChatGPT, Claude, and Gemini.  
> No API keys. No subscription fees. No cloud costs. Just your browser, locally.

---

## 🚀 What is Omni-LLM-Proxy?

**Stop paying for API keys.** Omni-LLM-Proxy is a lightweight FastAPI service that silently automates your web browsers to access ChatGPT, Claude, and Gemini. It exposes a **single REST API endpoint** (`/query`) that routes requests to your chosen LLM provider running in headless browsers.

Perfect for:
- ✅ **AI Projects** without API key licensing costs
- ✅ **Document Analyzers** that need multiple LLM backends
- ✅ **LangChain Integration** for local, cost-free inference
- ✅ **Development & Testing** without managing API quotas
- ✅ **Production Deployments** in private/air-gapped networks

---

## 🎯 Why Omni-LLM-Proxy?

| Feature | Omni-LLM-Proxy | Official APIs |
|---------|---|---|
| **Cost** | Free (hosting only) | $0.01-$0.15 per 1K tokens |
| **API Keys** | ❌ None needed | ✅ Required + managed |
| **Local Hosting** | ✅ Yes | ❌ Cloud only |
| **Multiple Providers** | ✅ ChatGPT, Claude, Gemini | ❌ One per API |
| **Concurrency / Queuing** | ✅ Built-in Async Worker Queue | ✅ Managed by vendor |
| **Streaming Detection** | ✅ Smart block validation | ✅ Built-in |
| **Privacy** | ✅ On your hardware | ❌ Cloud processing |

---

## 📦 Supported Providers

| Provider | Status | Features |
|----------|--------|----------|
| **ChatGPT** | ✅ Production Ready | Real-time detection (stop button monitoring) |
| **Claude** | ✅ Production Ready | Configurable via CSS selectors |
| **Gemini** | ✅ Production Ready | Google AI integration |

---

## 🏗️ Architecture

```
┌─ Your Application ──────────────┐
│                                 │
│  AI Document Analyzer           │
│  LangChain Integration          │
│  Coding Assistant               │
│  Any HTTP Client                │
│                                 │
└──────────── POST /query ─────────┘
              ▼
┌─────────────────────────────────┐
│   Omni-LLM-Proxy (FastAPI)      │
│                                 │
│  [ Queueing Service ]           │
│         │                       │
│  ├─ ChatGPT Provider            │
│  ├─ Claude Provider             │
│  └─ Gemini Provider             │
│                                 │
│  (Sequential background worker) │
└──────────┬──────────────────────┘
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
 🌐 ChatGPT  📚 Claude  🔍 Gemini
  Browser   Browser    Browser
```

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.12+
- Browser profiles pre-logged in (Chrome/Chromium)

### Installation

```bash
# Clone the repository
git clone https://github.com/yashyc7/omni-llm-proxy.git
cd omni-llm-proxy

# Install dependencies
pip install -r requirements.txt
# OR using uv (faster):
uv sync

# Create .env file
cat > .env << EOF
DEFAULT_PROVIDER=chatgpt
PORT=5000
HEADLESS=false
RESPONSE_TIMEOUT=60000
EOF

# Run with default provider (ChatGPT)
uv run python main.py

# Or specify a provider
uv run python main.py gemini
uv run python main.py claude
```

---

## 🔌 API Endpoints

### Health Check
```bash
GET http://localhost:5000/health

Response:
{
  "status": "ok",
  "provider": "chatgpt",
  "available": ["chatgpt", "claude", "gemini"]
}
```

### Query LLM
```bash
POST http://localhost:5000/query
Content-Type: application/json

{
  "query": "What is the capital of France?"
}

Response:
{
  "response": "Paris is the capital of France.",
  "provider": "chatgpt"
}
```

---

## 📚 Usage Examples

### 1. **Basic HTTP Request**

```bash
# Using curl
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Write a Python async function"}'

# Response includes real newlines (parsed from \n)
{
  "response": "async def fetch_data(url):\n    async with httpx.AsyncClient() as client:\n        return await client.get(url)",
  "provider": "chatgpt"
}
```

### 2. **Python Integration**

```python
import requests
import json

BASE_URL = "http://localhost:5000"

def query_llm(question: str, provider: str = "chatgpt"):
    response = requests.post(
        f"{BASE_URL}/query",
        json={"query": question},
        headers={"Content-Type": "application/json"}
    )
    return response.json()

# Usage
result = query_llm("How do I use asyncio in Python?")
print(result["response"])  # Real newlines, not \n strings
```

### 3. **LangChain Integration** 🎯

```python
from langchain_community.llms.base import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
import requests
from typing import Optional, Any, List

class OmniLLMProxy(LLM):
    """LangChain wrapper for Omni-LLM-Proxy"""
    
    base_url: str = "http://localhost:5000"
    provider: str = "chatgpt"
    
    @property
    def _llm_type(self) -> str:
        return "omni-llm-proxy"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        response = requests.post(
            f"{self.base_url}/query",
            json={"query": prompt}
        )
        return response.json()["response"]

# Usage in LangChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = OmniLLMProxy(provider="claude")

prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a short article about {topic}"
)

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(topic="AI Safety")
print(result)
```

### 4. **Document Analysis Project**

```python
# analyze_document.py
from fastapi import FastAPI, File, UploadFile
import requests
import PyPDF2

app = FastAPI()
LLM_API = "http://localhost:5000"

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    # Extract text from PDF
    pdf_reader = PyPDF2.PdfReader(file.file)
    text = "".join(page.extract_text() for page in pdf_reader.pages)
    
    # Query Omni-LLM-Proxy
    response = requests.post(
        f"{LLM_API}/query",
        json={"query": f"Summarize this document:\n\n{text[:5000]}"}
    )
    
    summary = response.json()["response"]
    return {"summary": summary, "provider": response.json()["provider"]}
```

### 5. **Environment Variable Switching**

```bash
# Run with different providers without code changes
DEFAULT_PROVIDER=gemini uv run python main.py
DEFAULT_PROVIDER=claude PORT=8000 uv run python main.py
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# .env file
DEFAULT_PROVIDER=chatgpt        # chatgpt | gemini | claude
PORT=5000                       # API server port
HEADLESS=false                  # true for production, false for debugging
RESPONSE_TIMEOUT=60000          # ms to wait for LLM response
```

### Provider-Specific Configuration

Edit `config.py` to customize selectors:

```python
PROVIDERS: dict[str, ProviderConfig] = {
    "chatgpt": ProviderConfig(
        url="https://chat.openai.com",
        input_selector="#prompt-textarea",
        submit_selector="#composer-submit-button",
        response_selector=".markdown.prose",
        done_selector="#composer-submit-button:not([disabled])",
        system_prompt="Be concise and direct.",
    ),
    # Add custom selectors for UI changes
}
```

---

## 🖥️ Browser Profile Setup

1. **Manually log in to each provider** in your browser:
   ```bash
   # Open Chrome profiles directory
   ~/.chrome_profiles/chatgpt/
   ~/.chrome_profiles/claude/
   ~/.chrome_profiles/gemini/
   ```

2. **Log in and save credentials** in each profile like we genreally do with google etc 

3. **Omni-LLM-Proxy will reuse these profiles** itself automatically

---

## 🐛 Troubleshooting


### Issue: "Partial response received"
```
Solution: Provider-specific streaming detection is enabled by default
Check: Is the stop button visible in the LLM UI during generation?
```

### Issue: "Selector not found"
```
Solution: Update selectors in config.py after UI changes
Use DevTools (F12) to inspect the new selectors
```

---

## 🔒 Security & Best Practices

✅ **Do:**
- Run on localhost or private network only
- Use `HEADLESS=true` in production
- Keep browser profiles secure (`~/.chrome_profiles`)
- Use environment variables for sensitive data

❌ **Don't:**
- Expose the API publicly without authentication
- Store credentials in version control
- Use on untrusted networks
- Share browser profiles across users

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
   ```bash
   git clone https://github.com/yashyc7/omni-llm-proxy.git
   cd omni-llm-proxy
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and test thoroughly
   ```bash
   uv run pytest  # Run tests
   uv run ruff format .  # Format code
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add support for [feature]"
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** with a clear description

### Ways to Contribute:
- 🐛 Report bugs and edge cases
- ✨ Add new LLM providers (Llama, Mistral, etc.)
- 📖 Improve documentation
- 🚀 Optimize performance
- 🔒 Enhance security
- 🧪 Add test cases

---

## 💰 Sponsorship

If Omni-LLM-Proxy helps you save on API costs, consider supporting the project:

- ⭐ **Star this repository** on GitHub
- 💬 **Share your success stories**
- 🐛 **Report issues and contribute**
- 🎓 **Teach others how to use it**

### Support the Project:
- [Buy me a coffee ☕](https://buymeacoffee.com/yashyc7)
- [Contribute code or documentation](https://github.com/yashyc7/omni-llm-proxy)

---

## 📊 Real-World Savings

### Cost Comparison (1M tokens/month)

| Service | Cost | With Omni-LLM-Proxy |
|---------|------|-------------------|
| ChatGPT API | $5-15/month | **Free** (server only) |
| Claude API | $1-25/month | **Free** (server only) |
| Gemini API | $0.075-1.50/month | **Free** (server only) |
| **Total** | **$6.075-41.50** | **~$5-20** (hosting) |
| **Savings** | — | **75-95%** 📉 |

---

## 📝 License

MIT License — See [LICENSE](LICENSE) file for details.

---

## 🎓 How It Works (Under the Hood)

```
1. Request arrives at /query endpoint
   ├─ FastAPI validates JSON schema
   ├─ QueryService intercepts and safely delegates request
   │
2. Asynchronous Background Queueing
   ├─ Request is instantly wrapped in a Future & enqueued
   ├─ A dedicated `asyncio` background worker isolates browser operations
   ├─ Concurrent requests are systematically processed in chronological order
   │
3. Provider automates Playwright browser
   ├─ Restores persistent login session automatically
   ├─ Injects predefined system prompt
   ├─ Types user query and submits
   │
4. Smart streaming detection (Robust Mode)
   ├─ Strictly validates the DOM for newly generated text blocks
   ├─ Monitors "Stop generating" button state
   ├─ Triggers API timeout explicitly if generation loops or fails
   │
5. Final response sent to client
   ├─ Parses the exact generation block
   ├─ Preserves newlines (\n in JSON)
   └─ Ready for downstream processing
```

---

## 🚀 Roadmap

- [ ] Support Llama, Mistral, local models
- [ ] Response caching (Redis)
- [ ] Batch query support
- [ ] WebSocket streaming API
- [ ] OpenAI API compatibility layer
---


<div align="center">

**Made with ❤️ for the AI community**

[⭐ Star us on GitHub](https://github.com/yashyc7/omni-llm-proxy)
</div>
