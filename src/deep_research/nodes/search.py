"""Нода поиска информации."""

from datetime import datetime

from rich.console import Console
from rich.table import Table

from deep_research.state import ResearchState, Finding
from deep_research.config import Config
from deep_research.search import TavilySearch

console = Console()


def search_node(state: ResearchState, config: Config) -> ResearchState:
    """Выполняет поиск по текущему шагу плана."""
    
    if state.status in ("cancelled", "completed"):
        return state
    
    # Определяем текущий шаг
    if state.current_step >= len(state.plan):
        return state
    
    current_query = state.plan[state.current_step]
    console.print(f"\n[bold cyan]Шаг {state.current_step + 1}/{len(state.plan)}:[/] {current_query}")
    
    try:
        # Инициализируем Tavily
        tavily = TavilySearch(config.search)
        
        # Выполняем поиск
        findings = tavily.search(current_query)
        
        # Добавляем к общему списку
        state.findings.extend(findings)
        state.search_calls += 1
        
        # Показываем результаты
        if findings:
            table = Table(title=f"Найдено {len(findings)} источников")
            table.add_column("#", style="cyan", width=3)
            table.add_column("Источник", style="green")
            table.add_column("Релевантность", style="yellow")
            
            for i, f in enumerate(findings[:5], 1):  # Показываем топ-5
                table.add_row(
                    str(i),
                    f.title[:50] + "..." if len(f.title) > 50 else f.title,
                    f"{f.score:.2f}"
                )
            
            console.print(table)
        else:
            console.print("[yellow]Источники не найдены[/]")
        
    except Exception as e:
        console.print(f"[red]Ошибка поиска: {e}[/]")
    
    state.updated_at = datetime.now()
    return state
