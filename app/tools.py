import os
from langchain_tavily import TavilySearch
from langchain_community.tools import DuckDuckGoSearchRun

def search_web(query: str) -> str:
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        try:
            tool = TavilySearch(max_results=3)
            results = tool.invoke({"query": query})

            return f"Search Results for '{query}':\n{str(results)}"
        except Exception:
            pass

    try:
        return DuckDuckGoSearchRun().invoke(query)
    except Exception as e:
        return f"Search Error: {str(e)}"