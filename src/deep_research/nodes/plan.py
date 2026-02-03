"""Нода планирования исследования."""

import uuid
from datetime import datetime

from rich.console import Console
from rich.panel import Panel

from deep_research.state import ResearchState
from deep_research.config import Config

console = Console()


def plan_node(state: ResearchState, config: Config) -> ResearchState:
    """Генерирует план исследования.
    
    Для MVP — простой план из 3 шагов.
    В будущем здесь будет LLM для генерации интеллектуального плана.
    """
    # Если уже есть план — пропускаем
    if state.plan:
        return state
    
    # Генерируем ID сессии
    if not state.session_id:
        state.session_id = str(uuid.uuid4())[:8]
    
    # Простой план по умолчанию
    state.plan = [
        f"Обзор: основные концепции и определения по теме '{state.query}'",
        f"Анализ: сравнение подходов и методологий",
        f"Практика: реализации, код, кейсы использования"
    ]
    
    # Показываем план пользователю
    console.print()
    console.print(Panel(
        f"[bold blue]Запрос:[/] {state.query}\n\n"
        f"[bold green]План исследования:[/]\n" +
        "\n".join(f"  {i+1}. {step}" for i, step in enumerate(state.plan)),
        title=f"Research Session: {state.session_id}",
        border_style="blue"
    ))
    
    if config.ui.interactive:
        response = console.input(
            "\n[yellow]Продолжить с этим планом? (y/n/редактировать): [/]"
        ).strip().lower()
        
        if response == 'n':
            console.print("[red]Исследование отменено[/]")
            state.status = "cancelled"
        elif response and response != 'y':
            # Пользователь хочет изменить план
            console.print("[yellow]Редактирование плана пока не реализовано, используем текущий[/]")
    
    state.updated_at = datetime.now()
    return state
