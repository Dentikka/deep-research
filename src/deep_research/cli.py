"""CLI интерфейс для deep research."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from deep_research.graph import create_research_graph
from deep_research.state import ResearchState
from deep_research.config import load_config, Config
from deep_research.storage import ResearchStorage

app = typer.Typer(help="Personal Deep Research Agent")
console = Console()


def get_config() -> Config:
    """Загружает конфигурацию или показывает ошибку."""
    try:
        return load_config()
    except FileNotFoundError as e:
        console.print(f"[red]Ошибка:[/] {e}")
        raise typer.Exit(1)


@app.command()
def query(
    q: str = typer.Argument(..., help="Research query"),
    interactive: bool = typer.Option(True, "--interactive/--auto", help="Интерактивный режим"),
):
    """Запускает новое исследование по запросу."""
    config = get_config()
    config.ui.interactive = interactive
    
    # Создаем начальное состояние
    initial_state = ResearchState(query=q)
    
    # Создаем и запускаем граф
    try:
        graph = create_research_graph(config)
        
        # Конфигурация для checkpointer
        thread_config = {"configurable": {"thread_id": initial_state.session_id}}
        
        console.print(f"[bold green]Запуск исследования:[/] {q}")
        console.print(f"[dim]Session ID: {initial_state.session_id}[/]")
        
        # Запускаем граф
        final_state = None
        for event in graph.stream(initial_state, thread_config):
            # LangGraph возвращает события для каждой ноды
            if "__end__" not in event:
                # Получаем последнее состояние
                final_state = list(event.values())[0] if event else None
        
        if final_state and final_state.status == "completed":
            console.print(f"\n[bold green]✓ Исследование завершено![/]")
            if final_state.report_path:
                console.print(f"[dim]Отчет сохранен: {final_state.report_path}[/]")
        elif final_state and final_state.status == "cancelled":
            console.print("\n[yellow]Исследование отменено[/]")
        
    except Exception as e:
        console.print(f"[red]Ошибка:[/] {e}")
        raise typer.Exit(1)


@app.command()
def list(
    status: Optional[str] = typer.Option(None, "--status", help="Фильтр по статусу"),
):
    """Список сохраненных исследований."""
    config = get_config()
    storage = ResearchStorage(config.storage.db_path)
    
    sessions = storage.list_sessions(status)
    
    if not sessions:
        console.print("[yellow]Нет сохраненных исследований[/]")
        return
    
    table = Table(title="Research Sessions")
    table.add_column("ID", style="cyan")
    table.add_column("Query", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Updated", style="dim")
    
    for row in sessions:
        table.add_row(row[0], row[1][:40], row[2], row[4][:16])
    
    console.print(table)


@app.command()
def resume(
    session_id: str = typer.Argument(..., help="ID сессии для продолжения"),
):
    """Продолжает сохраненное исследование."""
    config = get_config()
    storage = ResearchStorage(config.storage.db_path)
    
    state = storage.load_session(session_id)
    if not state:
        console.print(f"[red]Сессия {session_id} не найдена[/]")
        raise typer.Exit(1)
    
    console.print(f"[bold]Возобновление:[/] {state.query}")
    # TODO: Реализовать продолжение
    console.print("[yellow]Пока не реализовано[/]")


def main():
    app()


if __name__ == "__main__":
    main()
