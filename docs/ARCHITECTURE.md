# ARCHITECTURE — Архитектура проекта

## Общая схема

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                           │
│                    (Rich + argparse)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                      LangGraph Engine                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Plan    │→│ Search   │→│ Analyze  │→│ Report   │   │
│  │  Node    │  │  Node    │  │  Node    │  │  Node    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         ↑                                    │              │
│         └──────── Human-in-the-loop ─────────┘              │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼─────┐ ┌───▼────┐ ┌─────▼──────┐
│   Tavily    │ │ GitHub │ │   arXiv    │
│   Search    │ │ Search │ │   Search   │
└─────────────┘ └────────┘ └────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    Persistence Layer                        │
│                      (SQLite)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Research   │  │   Sources    │  │   Reports    │      │
│  │   Sessions   │  │   (raw)      │  │  (processed) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## State Machine (LangGraph)

### Состояния (States)

```python
class ResearchState(BaseModel):
    query: str                    # Исходный запрос
    plan: List[str]              # План исследования
    current_step: int            # Текущий шаг плана
    findings: List[Finding]      # Найденные источники
    user_feedback: Optional[str] # Обратная связь
    final_report: Optional[str]  # Итоговый отчет
    metadata: Dict               # Время, токены и т.д.
```

### Nodes

1. **plan_node**
   - Генерирует план исследования
   - Запрашивает подтверждение у пользователя
   - Output: список шагов

2. **search_node**
   - Выполняет поиск по текущему шагу
   - Использует Tavily (и другие источники в будущем)
   - Output: список Finding

3. **analyze_node**
   - Анализирует найденные источники
   - Оценивает: достаточно ли информации?
   - Output: continue или finalize

4. **report_node**
   - Генерирует структурированный отчет
   - Сохраняет в SQLite и файл

### Edges

- Conditional edges после analyze_node:
  - Если need_more_info → search_node (следующий шаг)
  - Если достаточно → report_node

## Папки проекта

```
deep-research/
├── src/
│   └── deep_research/
│       ├── __init__.py
│       ├── graph.py          # LangGraph определение
│       ├── state.py          # Pydantic модели
│       ├── nodes/            # Ноды графа
│       │   ├── __init__.py
│       │   ├── plan.py
│       │   ├── search.py
│       │   ├── analyze.py
│       │   └── report.py
│       ├── search/           # Интеграции поиска
│       │   ├── __init__.py
│       │   ├── tavily.py     # Уже работает
│       │   ├── github.py     # TODO
│       │   └── arxiv.py      # TODO
│       ├── storage.py        # SQLite persistence
│       ├── cli.py            # CLI интерфейс
│       └── config.py         # Конфигурация
├── config/
│   └── config.toml           # Пользовательские настройки
├── data/                     # SQLite БД
│   └── research.db
├── outputs/                  # Сгенерированные отчеты
├── tests/
├── docs/                     # Документация проекта
│   ├── CONCEPT.md
│   ├── TODO.md
│   ├── ROADMAP.md
│   └── ARCHITECTURE.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── README.md
```

## Поток данных

1. Пользователь запускает `deep-research query "тема"`
2. CLI создает ResearchState, сохраняет в SQLite
3. LangGraph запускает plan_node
4. План показывается пользователю, запрашивается подтверждение
5. Цикл: search → analyze → (human-in-the-loop)
6. Когда достаточно информации → report_node
7. Отчет сохраняется и показывается пользователю
8. Сессия помечается как completed в SQLite

## Технические детали

### SQLite Schema

```sql
CREATE TABLE research_sessions (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    state_json TEXT NOT NULL,  -- сериализованный ResearchState
    status TEXT,  -- active, paused, completed
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE findings (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    source TEXT,  -- tavily, github, arxiv
    url TEXT,
    title TEXT,
    content TEXT,
    relevance_score FLOAT,
    FOREIGN KEY (session_id) REFERENCES research_sessions(id)
);
```

### Config Format (config.toml)

```toml
[llm]
provider = "openai"  # или anthropic, local
model = "gpt-4o"
api_key = ""  # заполняет пользователь

[search]
tavily_api_key = ""  # уже есть у пользователя
max_results = 10

[storage]
db_path = "data/research.db"

[output]
format = "markdown"  # или json, или both
save_path = "outputs/"
```
