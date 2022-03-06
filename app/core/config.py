import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
from linebot import LineBotApi, WebhookHandler

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "api.ptt.cx"
    SERVER_HOST: AnyHttpUrl = "https://api.ptt.cx"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ['http://localhost']

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Ark Backend"
    SENTRY_DSN: Optional[HttpUrl] = ""
    IMG_PATH: str = "/var/www/ArkCard-Linebot/ArkCard-web/img/nft/"
    IMG_HOST: AnyHttpUrl = "https://ark.cards/img/nft/"

    # # bot config
    line_bot_api = LineBotApi(
        "SJT7VPT4RMQFLcS27jQBy3FcC24gtDrkcwJWZ5Xzqesr5T78LOKudHEJzt0k3b2S7"
        "n4KPwf27J7DVz2c8NQ4plSaaQylEeB1cYrfejaE/RPG/lCIQBYe4iBTzo26s4i2Pcm"
        "T89837per/lTyvhVIKAdB04t89/1O/w1cDnyilFU=")
    handler = WebhookHandler("411ae3ef7e766739ed2c2c27b249d010")


    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://choozmo:pAssw0rd@db.ptt.cx:3306/arkcard?charset=utf8mb4"
    # POSTGRES_SERVER: str 
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str
    # POSTGRES_DB: str
    # SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    # @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    # def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
    #     if isinstance(v, str):
    #         return v
    #     return PostgresDsn.build(
    #         scheme="postgresql",
    #         user=values.get("POSTGRES_USER"),
    #         password=values.get("POSTGRES_PASSWORD"),
    #         host=values.get("POSTGRES_SERVER"),
    #         path=f"/{values.get('POSTGRES_DB') or ''}",
    #     )

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 465
    SMTP_HOST: Optional[str] = 'smtp.gmail.com'
    SMTP_USER: Optional[str] = ''
    SMTP_PASSWORD: Optional[str] = 'ckmspyijofyavuwg'
    EMAILS_FROM_EMAIL: Optional[EmailStr] = 'verify@choozmo.com'
    EMAILS_FROM_NAME: Optional[str] = 'Choozmo Team'

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/home/conrad/creator/app/email-templates/build"
    # EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = True

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "conradlan@choozmo.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr = "conradlan@choozmo.com"
    FIRST_SUPERUSER_PASSWORD: str = "test123"
    USERS_OPEN_REGISTRATION: bool = True

    class Config:
        case_sensitive = True


settings = Settings()
