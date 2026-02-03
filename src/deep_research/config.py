"""Загрузка и валидация конфигурации."""

import os
from pathlib import Path
from typing import Optional

import toml
from pydantic import BaseModel, Field, validator


class LLMConfig(BaseModel):
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4o-mini")
    api_key: str = Field(default="")


class SearchConfig(BaseModel):
    tavily_api_key: str = Field(default="")
    max_results: int = Field(default=10)
    search_depth: str = Field(default="advanced")


class StorageConfig(BaseModel):
    db_path: str = Field(default="data/research.db")


class OutputConfig(BaseModel):
    format: str = Field(default="both")
    save_path: str = Field(default="outputs/")


class UIConfig(BaseModel):
    interactive: bool = Field(default=True)


class Config(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    
    @validator("search")
    def check_tavily_key(cls, v: SearchConfig) -> SearchConfig:
        """Проверяем наличие ключа Tavily."""
        if not v.tavily_api_key:
            env_key = os.getenv("TAVILY_API_KEY")
            if env_key:
                v.tavily_api_key = env_key
        return v


def load_config(config_path: Optional[str] = None) -> Config:
    """Загружает конфигурацию из TOML файла."""
    if config_path is None:
        # Ищем в стандартных местах
        repo_root = Path(__file__).parent.parent.parent
        config_path = repo_root / "config" / "config.toml"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            "Copy config/config.example.toml to config/config.toml and fill in your API keys"
        )
    
    with open(config_path, "r") as f:
        data = toml.load(f)
    
    return Config(**data)
