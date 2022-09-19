import secrets
from urllib.parse import unquote
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator, Field
from cryptography.fernet import Fernet


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENCODING_KEY: Optional[bytes] = None

    @validator("ENCODING_KEY", pre=True)
    def generate_db_encoding_key(cls, v: Optional[str]) -> bytes:
        if isinstance(v, str):
            return v.encode()
        return Fernet.generate_key()

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:80"]'
    BACKEND_CORS_ORIGINS: Union[str, List[AnyHttpUrl]] = Field(...)

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "GreenPlum Permission Manager"

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> str:
        if isinstance(v, str):
            return v
        return unquote(
            PostgresDsn.build(
                scheme="postgresql",
                user=values["POSTGRES_USER"],
                password=values["POSTGRES_PASSWORD"],
                host=values["POSTGRES_SERVER"],
                port=f"{values['POSTGRES_PORT']}",
                path=f"/{values['POSTGRES_DB']}",
            )
        )

    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    LOGGING_DEBUG: bool = False
    INSTALL_DBLINK: bool = True
    GRANT_WITH_ADMIN_OPTION: bool = False
    DEEP_REVOKE: bool = True

    AUTH_PROVIDER: str = "local"  # ldap

    @validator("AUTH_PROVIDER", pre=True)
    def validate_auth_provider(cls, v: str) -> str:
        ldap = v.lower()
        if ldap in ('local', 'ldap'):
            return ldap
        raise ValueError(v)

    AUTH_OPEN_REGISTRATION: bool = False
    AUTH_REFRESH_PASSWORD: bool = False

    LDAP_HOST: Optional[str] = None
    LDAP_USER_SEARCH_BASE: Optional[str] = None
    LDAP_USER_SEARCH_FILTER: Optional[str] = None
    LDAP_USER_ATTRS: Union[str, List[str], None] = None

    @validator("LDAP_HOST", "LDAP_USER_SEARCH_BASE", "LDAP_USER_SEARCH_FILTER", pre=True)
    def ldap_params_may_missing(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        ldap: str = values["AUTH_PROVIDER"]
        if ldap != "ldap":
            return None
        elif isinstance(v, str):
            return v
        raise ValueError(v)

    @validator("LDAP_USER_ATTRS", pre=True)
    def ldap_params_user_attrs(
        cls, v: Union[str, List[str], None], values: Dict[str, Any]
    ) -> Union[List[str], str, None]:
        ldap: str = values["AUTH_PROVIDER"]
        if ldap != "ldap":
            return None
        elif isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True


settings = Settings()
