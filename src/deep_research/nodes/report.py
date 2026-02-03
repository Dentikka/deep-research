"""Нода генерации отчета."""

import json
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

from deep_research.state import ResearchState
from deep_research.config import Config
from deep_research.storage import ResearchStorage

console = Console()


def generate_markdown_report(state: ResearchState) -> str:
    """Генерирует Markdown отчет."""
    report = f"""# Research Report: {state.query}

**Session ID:** {state.session_id}  
**Generated:** {state.updated_at.strftime("%Y-%m-%d %H:%M")}  
**Sources found:** {len(state.findings)}

## Summary

Исследование по теме "{state.query}" охватило {len(state.plan)} направления.

## Findings

"""
    
    # Группируем по релевантности
    sorted_findings = sorted(state.findings, key=lambda x: x.score, reverse=True)
    
    for i, f in enumerate(sorted_findings[:15], 1):  # Топ-15
        report += f"""### {i}. {f.title}

- **Source:** {f.source}
- **URL:** {f.url}
- **Relevance:** {f.score:.3f}

{f.content[:500]}{"..." if len(f.content) > 500 else ""}

---

"""
    
    report += f"""## Raw Data

```json
{json.dumps({
    "query": state.query,
    "plan": state.plan,
    "total_findings": len(state.findings),
    "search_calls": state.search_calls
}, indent=2, ensure_ascii=False)}
```
"""
    
    return report


def report_node(state: ResearchState, config: Config) -> ResearchState:
    """Генерирует и сохраняет отчет."""
    
    if state.status == "cancelled":
        return state
    
    console.print("\n[bold green]Генерация отчета...[/]")
    
    # Генерируем отчет
    report_md = generate_markdown_report(state)
    state.final_report = report_md
    
    # Сохраняем в файл
    output_dir = Path(config.output.save_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{state.session_id}_{state.query[:30].replace(' ', '_')}"
    
    if config.output.format in ("markdown", "both"):
        md_path = output_dir / f"{filename}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        state.report_path = str(md_path)
        console.print(f"[green]Markdown сохранен:[/] {md_path}")
    
    if config.output.format in ("json", "both"):
        json_path = output_dir / f"{filename}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(state.model_dump(), f, indent=2, default=str, ensure_ascii=False)
        console.print(f"[green]JSON сохранен:[/] {json_path}")
    
    # Сохраняем в БД
    storage = ResearchStorage(config.storage.db_path)
    state.status = "completed"
    storage.save_session(state)
    
    # Показываем превью
    console.print("\n[bold]Превью отчета:[/]")
    console.print(Markdown(report_md[:1500] + "..."))
    
    state.updated_at = datetime.now()
    return state
