"""Граф LangGraph для deep research."""

from typing import Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from deep_research.state import ResearchState
from deep_research.config import Config
from deep_research.nodes import plan_node, search_node, analyze_node, report_node


def should_continue(state: ResearchState) -> Literal["search", "report"]:
    """Определяет, куда идти дальше."""
    if state.status in ("cancelled", "completed"):
        return "report"
    if state.status == "ready_for_report":
        return "report"
    return "search"


def create_research_graph(config: Config):
    """Создает и возвращает скомпилированный граф."""
    
    # Создаем граф
    workflow = StateGraph(ResearchState)
    
    # Добавляем ноды
    # Используем lambda для передачи config в ноды
    workflow.add_node("plan", lambda state: plan_node(state, config))
    workflow.add_node("search", lambda state: search_node(state, config))
    workflow.add_node("analyze", lambda state: analyze_node(state, config))
    workflow.add_node("report", lambda state: report_node(state, config))
    
    # Добавляем edges
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "search")
    workflow.add_edge("search", "analyze")
    
    # Conditional edge из analyze
    workflow.add_conditional_edges(
        "analyze",
        should_continue,
        {
            "search": "search",
            "report": "report"
        }
    )
    
    workflow.add_edge("report", END)
    
    # Компилируем с памятью (для MVP используем in-memory, позже SQLite)
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app
