"""Интеграция с Tavily для web поиска."""

from typing import List

from tavily import TavilyClient

from deep_research.state import Finding
from deep_research.config import SearchConfig


class TavilySearch:
    """Поиск через Tavily API."""
    
    def __init__(self, config: SearchConfig):
        if not config.tavily_api_key:
            raise ValueError(
                "Tavily API key not configured. "
                "Add it to config/config.toml or set TAVILY_API_KEY env var"
            )
        self.client = TavilyClient(api_key=config.tavily_api_key)
        self.max_results = config.max_results
        self.search_depth = config.search_depth
    
    def search(self, query: str) -> List[Finding]:
        """Выполняет поиск и возвращает найденные источники."""
        response = self.client.search(
            query=query,
            max_results=self.max_results,
            search_depth=self.search_depth,
            include_answer=False,  # Нам нужны только источники
        )
        
        findings = []
        for result in response.get("results", []):
            findings.append(Finding(
                source="tavily",
                url=result.get("url", ""),
                title=result.get("title", "Untitled"),
                content=result.get("content", ""),
                score=result.get("score", 0.0),
                metadata={
                    "raw_content": result.get("raw_content", "")
                }
            ))
        
        return findings
