from phi.agent import Agent
from phi.model.groq import Groq
from dotenv import load_dotenv
from phi.tools.yfinance import YFinanceTools
load_dotenv()

test_agent=Agent(
    model=Groq(
    id="qwen/qwen3.6-27b"),
    tools=[YFinanceTools(
        stock_price=True,
        analyst_recommendations=True,
        stock_fundamentals=True
        )],
    show_tool_calls=True,
    markdown=True,
    instructions=["Always create tables for comparisons"],
)

test_agent.print_response("summarise and compare the analyst recommendations for the stocks of Apple anf Tesla")