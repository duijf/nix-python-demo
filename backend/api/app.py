from __future__ import annotations

import dataclasses
import enum
import json
import logging
import typing as t
from urllib.parse import urlencode

from cryptography.fernet import InvalidToken
from fastapi import APIRouter, FastAPI
from fastapi.param_functions import Depends
from funcy import lmap, reraise  # type: ignore
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    Response,
)
from starlette.staticfiles import StaticFiles

from api.config import Config, get_config
from api.github import (
    GitHubError,
    fetch_github_access_token,
    fetch_github_user,
)
from api.postgres import Connection, Postgres, connect_and_migrate
from api.session import NewSession, Session, SessionProblem

logger = logging.getLogger(__name__)
router = APIRouter()


class State(BaseModel):
    redirect: str

    def encrypt(self, config: Config) -> str:
        json_bytes = self.json().encode("utf-8")
        ciphertext_bytes = config.state_encryption.encrypt(json_bytes)
        return ciphertext_bytes.decode("utf-8")

    @staticmethod
    def decrypt(config: Config, ciphertext: str) -> State:
        with reraise(
            InvalidToken,
            Invalid(parameter="state", detail="could_not_decrypt"),
        ):
            json_val = config.state_encryption.decrypt(
                ciphertext.encode("utf-8")
            )
        return State(**json.loads(json_val))


@dataclasses.dataclass
class Missing(Exception):
    parameter: str

    def as_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": "missing_parameter",
                "parameter": self.parameter,
            },
        )


@dataclasses.dataclass
class Invalid(Exception):
    parameter: str
    detail: str

    def as_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_parameter",
                "parameter": self.parameter,
                "detail": self.detail,
            },
        )


@router.get("/")
async def get_home(
    session: t.Union[SessionProblem, Session] = Depends(Session.optional),
) -> Response:
    if isinstance(session, Session):
        return RedirectResponse("/app")

    return HTMLResponse('Want to <a href="/login">log in</a>?')


@router.get("/app")
async def get_app(
    conn: Connection = Depends(Postgres.connection),
    session: Session = Depends(Session.authenticated),
) -> Response:
    logger.info(session.session_id)

    users = await conn.fetch(
        "SELECT user_id, username, avatar_url FROM users;"
    )
    return JSONResponse(content={"users": lmap(dict, users)})


@router.get("/login")
async def github_redirect_oauth(
    config: Config = Depends(get_config),
) -> Response:
    state = State(redirect="/").encrypt(config)

    query_params = {
        "client_id": config.github.app_client_id,
        "redirect_uri": f"{config.api_url}/api/complete/github",
        "state": state,
    }
    redirect_url = (
        f"{config.github.oauth_login_endpoint}?{urlencode(query_params)}"
    )
    return RedirectResponse(redirect_url)


class GitHubOAuthError(enum.Enum):
    ACCESS_DENIED = "access_denied"
    REDIRECT_URI_MISMATCH = "redirect_uri_mismatch"


@router.get("/api/complete/github")
async def github_callback(
    code: t.Optional[str] = None,
    state: t.Optional[str] = None,
    error: t.Optional[GitHubOAuthError] = None,
    config: Config = Depends(get_config),
    conn: Connection = Depends(Postgres.connection),
) -> Response:
    if error:
        logger.error(f"Error from GitHub: {error}")
        return JSONResponse(status_code=400, content={"error": error.value})
    if state is None:
        raise Missing("state")
    if code is None:
        raise Missing("code")

    state: State = State.decrypt(config, state)
    token = fetch_github_access_token(config.github, code)
    user = fetch_github_user(config.github, token)

    query = """
        INSERT INTO users (username, avatar_url)
        VALUES ($1, $2)
        ON CONFLICT (username) DO UPDATE SET user_id = users.user_id
        RETURNING user_id;"""

    user_id = await conn.fetchval(
        query,
        user.login,
        user.avatar_url,
    )

    session = await NewSession(user_id=user_id).create(conn)
    return RedirectResponse(
        state.redirect, headers={"Set-Cookie": session.as_cookie()}
    )


def create_app() -> FastAPI:
    config = get_config()

    async def on_startup() -> None:
        await connect_and_migrate(config.postgres)

    async def on_shutdown() -> None:
        await Postgres.disconnect()

    async def handle_github_error(_: Request, exc: GitHubError) -> Response:
        return exc.as_response()

    async def handle_missing(_: Request, exc: Missing) -> Response:
        return exc.as_response()

    async def handle_invalid(_: Request, exc: Invalid) -> Response:
        return exc.as_response()

    app = FastAPI(
        openapi_url=None,
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
        exception_handlers={
            GitHubError: handle_github_error,
            Missing: handle_missing,
            Invalid: handle_invalid,
        },
    )

    app.mount(
        "/static", app=StaticFiles(directory=config.static_dir, html=True)
    )

    app.include_router(router)

    return app
