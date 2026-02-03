"""Нода анализа результатов."""

from datetime import datetime

from rich.console import Console

from deep_research.state import ResearchState
from deep_research.config import Config

console = Console()


def analyze_node(state: ResearchState, config: Config) -> ResearchState:
    """Анализирует результаты и решает, что делать дальше.
    
    Для MVP — простая логика: переходим к следующему шагу
    или завершаем если это последний шаг.
    """
    
    if state.status in ("cancelled", "completed"):
        return state
    
    console.print(f"\n[bold]Анализ результатов...[/]")
    console.print(f"Всего источников: {len(state.findings)}")
    
    # Спрашиваем пользователя в интерактивном режиме
    if config.ui.interactive:
        console.print("\n[cyan]Действия:[/]")
        console.print("  [1] Перейти к следующему шагу")
        console.print("  [2] Уточнить запрос и повторить поиск")
        console.print("  [3] Завершить и сгенерировать отчет")
        
        choice = console.input("\n[yellow]Выбор (1-3): [/]").strip()
        
        if choice == "2":
            state.user_feedback = console.input("[yellow]Уточнение: [/]").strip()
            # Не меняем current_step — повторим поиск
        elif choice == "3":
            state.status = "ready_for_report"
        else:
            # Переходим к следующему шагу
            state.current_step += 1
            if state.current_step >= len(state.plan):
                state.status = "ready_for_report"
    else:
        # Автоматический режим
        state.current_step += 1
        if state.current_step >= len(state.plan):
            state.status = "ready_for_report"
    
    state.updated_at = datetime.now()
    return state
