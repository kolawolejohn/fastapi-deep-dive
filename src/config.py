from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRY: int
    REFRESH_TOKEN_EXPIRY: int
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    JTI_EXPIRY: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool
    DOMAIN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()
