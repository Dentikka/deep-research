# TODO — Текущие работы

## Phase 0: Setup ✅

- [x] Создать рабочую директорию проекта
- [x] Создать документацию (CONCEPT, ROADMAP, ARCHITECTURE)
- [x] Клонировать репозиторий
- [x] Создать .gitignore
- [x] Создать структуру проекта
  - [x] src/deep_research/ — основной код
  - [x] src/deep_research/graph.py — граф LangGraph
  - [x] src/deep_research/state.py — Pydantic-модели состояния
  - [x] src/deep_research/search.py — Tavily интеграция
  - [x] src/deep_research/storage.py — SQLite persistence
  - [x] src/deep_research/cli.py — интерфейс командной строки
  - [x] config/ — конфигурационные файлы
  - [ ] tests/ — тесты
- [x] Создать pyproject.toml
- [x] Настроить config.toml с шаблоном

## Phase 1: MVP Core ✅

- [x] Реализовать базовый граф из 4 нод:
  - [x] Node: Plan — генерация плана исследования
  - [x] Node: Search — поиск через Tavily
  - [x] Node: Analyze — анализ результатов
  - [x] Node: Report — генерация отчета
- [x] State management через SQLite
- [x] Human-in-the-loop (input() между шагами)
- [x] Базовый CLI интерфейс

## Phase 2: Интеграция источников

- [ ] GitHub code search
- [ ] arXiv API
- [ ] Semantic Scholar

## Phase 3: Улучшения

- [ ] Web UI (Streamlit/Gradio)
- [ ] Экспорт в Notion/Google Docs
- [ ] Параллельный поиск

## Требуется вмешательство пользователя

- [ ] Добавить API ключи в config.toml (Tavily уже есть, нужен LLM ключ)
- [ ] Выбрать дефолтную LLM модель (OpenAI/Anthropic/локальная)
