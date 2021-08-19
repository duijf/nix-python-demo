from __future__ import annotations

import dataclasses
import enum
import logging
import typing as t
from urllib.parse import urlencode

import funcy  # type: ignore
import requests
from pydantic import BaseModel, BaseSettings
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class GitHubConfig(BaseSettings):
    host: str
    app_id: str
    app_client_id: str
    app_client_secret: str
    app_private_key: str

    @property
    def oauth_login_endpoint(self) -> str:
        return f"https://{self.host}/login/oauth/authorize"

    @property
    def oauth_access_token_endpoint(self) -> str:
        return f"https://{self.host}/login/oauth/access_token"

    @property
    def api_url(self) -> str:
        # GitHubConfig.com has the API on a subdomain. GitHubConfig Enterprise
        # has it on the same host.
        if self.host == "github.com":
            return "https://api.github.com"

        return f"https://{self.host}/api/v3"

    class Config:
        env_prefix = "github_"


class GitHubErrorCode(enum.Enum):
    BAD_VERIFICATION_CODE = "bad_verification_code"
    UNKNOWN_ERROR = "unknown_error"


@dataclasses.dataclass
class GitHubError(Exception):
    error_code: GitHubErrorCode

    @classmethod
    def from_json(cls, val: t.Dict[str, t.Any]) -> t.Optional[GitHubError]:
        if not isinstance(val, dict):
            return None

        if (error := val.get("error")) is None:
            return None

        with funcy.suppress(ValueError):
            return GitHubError(GitHubErrorCode(error))

        logger.error(f"Unknown GitHub error {error}")
        return GitHubError(GitHubErrorCode.UNKNOWN_ERROR)

    def as_response(self) -> JSONResponse:
        status_code = (
            500 if self.error_code == GitHubErrorCode.UNKNOWN_ERROR else 400
        )
        return JSONResponse(
            status_code=status_code, content={"error": self.error_code.value}
        )


class GitHubToken(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: t.Optional[str]
    refresh_token_expires_in: t.Optional[int]

    @property
    def headers(self) -> t.Dict[str, str]:
        return {"Authorization": f"token {self.access_token}"}


def fetch_github_access_token(github: GitHubConfig, code: str) -> GitHubToken:
    params = {
        "client_id": github.app_client_id,
        "client_secret": github.app_client_secret,
        "code": code,
    }
    url = f"{github.oauth_access_token_endpoint}?{urlencode(params)}"
    logger.info("Requesting GitHubConfig oauth token")
    resp = requests.post(url, headers={"Accept": "application/json"})
    resp.raise_for_status()

    if error := GitHubError.from_json(resp.json()):
        raise error

    token = GitHubToken(**resp.json())
    logger.debug(f"Received token {token}")
    return token


class GitHubUser(BaseModel):
    id: int
    login: str
    avatar_url: str


def fetch_github_user(github: GitHubConfig, token: GitHubToken) -> GitHubUser:
    resp = requests.get(f"{github.api_url}/user", headers=token.headers)
    resp.raise_for_status()
    return GitHubUser(**resp.json())
