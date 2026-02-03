"""Базовые тесты для deep research agent."""

import pytest
from deep_research.state import ResearchState, Finding
from deep_research.config import Config, LLMConfig, SearchConfig


def test_research_state_creation():
    """Тест создания состояния исследования."""
    state = ResearchState(query="test query")
    assert state.query == "test query"
    assert state.status == "active"
    assert len(state.findings) == 0


def test_finding_creation():
    """Тест создания Finding."""
    finding = Finding(
        source="tavily",
        url="https://example.com",
        title="Example",
        content="Test content",
        score=0.9
    )
    assert finding.source == "tavily"
    assert finding.score == 0.9


def test_config_defaults():
    """Тест дефолтной конфигурации."""
    config = Config()
    assert config.llm.provider == "openai"
    assert config.search.max_results == 10
    assert config.ui.interactive is True
