from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv
from phi.tools.yfinance import YFinanceTools
load_dotenv()


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
    debug_mode=True
)

try:
    agents_team.print_response("Summarise the analyst recommendations and share the latest information about Nvidia?")
except Exception as e:
    print(f"An error occurred: {e}")