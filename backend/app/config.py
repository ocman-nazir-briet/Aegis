from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Aegis Twin"
    app_version: str = "1.0.0"
    debug: bool = False

    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"

    github_token: Optional[str] = None
    gitlab_token: Optional[str] = None
    bitbucket_token: Optional[str] = None

    anthropic_api_key: Optional[str] = None

    max_diff_size: int = 500000
    simulation_timeout: int = 30
    ingestion_timeout: int = 300

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
