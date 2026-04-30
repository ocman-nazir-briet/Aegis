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
    jwt_expire_minutes: int = 60

    # Default users (override in .env)
    admin_username: str = "admin"
    admin_password: str = "changeme"
    viewer_username: str = "viewer"
    viewer_password: str = "viewonly"

    github_token: Optional[str] = None
    gitlab_token: Optional[str] = None
    bitbucket_token: Optional[str] = None

    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-haiku-4-5-20251001"

    max_diff_size: int = 500000
    simulation_timeout: int = 30
    ingestion_timeout: int = 300

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
