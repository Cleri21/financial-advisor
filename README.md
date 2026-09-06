Financial Advisor Agent

A multi-agent financial research assistant built with phidata (now Agno) and Groq, with a Streamlit chat UI.

The system uses a team of AI agents:

Financial Analyst — fetches live stock price, fundamentals, and analyst recommendations via yfinance
Web Researcher — searches the web for recent news via DuckDuckGo
Team Leader — delegates tasks to the two specialists above and combines their results into one polished, sourced answer
Features
Real-time stock data (price, P/E ratio, EPS, analyst buy/hold/sell breakdown)
Recent news search with source attribution
Multi-agent delegation (leader never touches tools directly, only assigns tasks)
Streamlit chat interface with message history
Token usage tracking per query, with a running session total and a downloadable CSV log
Graceful error handling so a failed tool call doesn't crash the whole app
Setup
1. Clone the repo
bash
git clone https://github.com/Cleri21/financial-advisor.git
cd financial-advisor
2. Install dependencies
bash
pip install phidata groq streamlit python-dotenv yfinance duckduckgo-search
3. Add your Groq API key

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here

Get a free key at console.groq.com/keys.

4. Run the app
bash
streamlit run app.py

This opens a browser tab with the chat interface. Try asking:

"Summarise analyst recommendations for Nvidia"
"What's the current price and latest news for Tesla?"
Project structure
financial-advisor/
├── app.py                 # Streamlit UI (main entry point)
├── financial_adivsors.py  # Terminal version of the multi-agent team
├── test.py                # Early single-agent test script
├── .env                   # Groq API key (not committed)
├── .gitignore
└── README.md
Notes on model choice

This project runs entirely on Groq's free tier, using openai/gpt-oss-20b (an open-weight model hosted by Groq — no OpenAI account or billing required). A few things worth knowing if you're extending this:

Reasoning models (e.g. Qwen) can burn output tokens on invisible <think> traces before producing a tool call, which can trip Groq's per-minute rate limits (429 errors) on multi-step, multi-agent tasks. openai/gpt-oss-20b is more token-efficient for this use case.
Not all Groq-hosted models support function/tool calling (e.g. groq/compound-mini does not). Stick to models confirmed to support tools if you swap models.
DuckDuckGo's search library is unofficial and can rate-limit (403) under heavy use. The web researcher agent is instructed to try at most 2 search queries before summarizing whatever it found, to avoid retry loops.
License

Personal learning project — no license specified.
