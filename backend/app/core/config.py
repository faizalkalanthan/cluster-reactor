from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "cluster-reactor-backend"
    app_version: str = "0.1.0"
    environment: str = "dev"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "cluster_reactor"
    db_user: str = "cluster_reactor"
    db_password: str = "cluster_reactor"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_pre_ping: bool = True
    db_auto_create_tables: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()