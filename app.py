import streamlit as st
import csv
import os
from datetime import datetime
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = "usage_log.csv"


def log_usage(prompt_text, input_tokens, output_tokens, total_tokens):
    """Append one row of token usage to a local CSV log."""
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "prompt", "input_tokens", "output_tokens", "total_tokens"])
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            prompt_text,
            input_tokens,
            output_tokens,
            total_tokens,
        ])

# ---------- Page setup ----------
st.set_page_config(page_title="Financial Advisor Agent", page_icon="\U0001F4C8", layout="centered")
st.title("\U0001F4C8 Financial Advisor Agent")
st.caption("Multi-agent team: Financial Analyst + Web Researcher, powered by Groq")

# ---------- Build the agent team once, cache it ----------
@st.cache_resource
def build_team():
    financial_agent = Agent(
        name="financial analyst",
        model=Groq(id="openai/gpt-oss-20b"),
        tools=[YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True
        )],
        show_tool_calls=True,
        markdown=True,
        instructions=["Always create tables for comparisons"],
    )

    web_researcher = Agent(
        name="web researcher",
        model=Groq(id="openai/gpt-oss-20b"),
        tools=[DuckDuckGo()],
        show_tool_calls=True,
        markdown=True,
        instructions=[
            "Always include sources of the information that you gather from any reputable outlet",
            "Try at most 2 search queries total. After that, immediately summarize whatever you found, even if incomplete or outdated. Do not keep retrying with different phrasing.",
        ],
    )

    agents_team = Agent(
        team=[financial_agent, web_researcher],
        model=Groq(id="openai/gpt-oss-20b"),
        show_tool_calls=True,
        markdown=True,
        instructions=[
            "Always include source of the information gathered",
            "Always create tables for comparisons",
            "You do not have direct access to any data tools. You must ALWAYS delegate data-gathering tasks to your team members using the transfer functions. Never attempt to call get_current_stock_price, get_stock_fundamentals, get_analyst_recommendations, duckduckgo_search, or duckduckgo_news yourself.",
        ],
    )
    return agents_team


agents_team = build_team()

# ---------- Chat-style history ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_tokens" not in st.session_state:
    st.session_state.session_tokens = {"input": 0, "output": 0, "total": 0}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Input box ----------
prompt = st.chat_input("Ask about a stock, e.g. 'Summarise analyst recommendations for Nvidia'")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            input_tokens = output_tokens = total_tokens = 0
            try:
                response = agents_team.run(prompt, stream=False)
                answer = response.content

                # Try to pull token usage off the response, if phidata exposes it
                metrics = getattr(response, "metrics", None) or {}
                input_tokens = sum(metrics.get("input_tokens", [0])) if metrics.get("input_tokens") else 0
                output_tokens = sum(metrics.get("output_tokens", [0])) if metrics.get("output_tokens") else 0
                total_tokens = sum(metrics.get("total_tokens", [0])) if metrics.get("total_tokens") else (input_tokens + output_tokens)

                if total_tokens:
                    st.session_state.session_tokens["input"] += input_tokens
                    st.session_state.session_tokens["output"] += output_tokens
                    st.session_state.session_tokens["total"] += total_tokens
                    log_usage(prompt, input_tokens, output_tokens, total_tokens)

            except Exception as e:
                answer = f"An error occurred: {e}"
        st.markdown(answer)

        if total_tokens:
            st.caption(f"\U0001F4CA This run: {input_tokens} in / {output_tokens} out / {total_tokens} total tokens")

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ---------- Sidebar ----------
with st.sidebar:
    st.subheader("About")
    st.write(
        "This assistant delegates to two specialist agents:\n\n"
        "- **Financial Analyst** — stock price, fundamentals, analyst recommendations (YFinance)\n"
        "- **Web Researcher** — recent news (DuckDuckGo)\n\n"
        "Running on Groq's free tier (openai/gpt-oss-20b)."
    )

    st.divider()
    st.subheader("\U0001F4CA Token usage (this session)")
    tok = st.session_state.session_tokens
    col1, col2, col3 = st.columns(3)
    col1.metric("Input", tok["input"])
    col2.metric("Output", tok["output"])
    col3.metric("Total", tok["total"])

    if os.path.isfile(LOG_FILE):
        with open(LOG_FILE, "rb") as f:
            st.download_button(
                "Download full usage log (CSV)",
                data=f,
                file_name="usage_log.csv",
                mime="text/csv",
            )

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.session_state.session_tokens = {"input": 0, "output": 0, "total": 0}
        st.rerun()