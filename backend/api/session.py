from __future__ import annotations

import datetime
import enum
import http.cookies
import logging
import typing as t
import uuid

from fastapi import Cookie, Depends, HTTPException
from pydantic import BaseModel

from api.postgres import Connection, Postgres

logger = logging.getLogger(__name__)


class SessionStatus(enum.Enum):
    VALID = "valid"
    REVOKED = "revoked"


class NewSession(BaseModel):
    user_id: int

    async def create(self, conn: Connection) -> Session:
        logger.info(f"Minting new session for user {self.user_id}")

        query = """
            INSERT INTO sessions (user_id, status)
            VALUES ($1, $2)
            RETURNING session_id, created_at, expires_at"""

        status = SessionStatus.VALID
        row = await conn.fetchrow(query, self.user_id, status.value)

        return Session(**{"user_id": self.user_id, "status": status, **row})


class SessionProblem(enum.Enum):
    MISSING = ("session_missing", 401)
    INVALID = ("session_invalid", 400)
    EXPIRED = ("session_expired", 401)

    def as_http_exception(self) -> HTTPException:
        # pylint: disable=unpacking-non-sequence
        detail, status_code = self.value
        return HTTPException(status_code=status_code, detail=detail)


class Session(NewSession):
    session_id: uuid.UUID
    created_at: datetime.datetime
    expires_at: datetime.datetime
    status: SessionStatus

    def as_cookie(self) -> str:
        # pylint: disable=unsubscriptable-object
        cookie: http.cookies.SimpleCookie[str] = http.cookies.SimpleCookie()

        now = datetime.datetime.now(datetime.timezone.utc)
        expires = (self.expires_at - now).total_seconds()

        cookie["session_id"] = self.session_id.hex
        cookie["session_id"]["expires"] = expires
        cookie["session_id"]["httponly"] = True
        cookie["session_id"]["secure"] = True
        # Needs to be `lax` instead of `strict` to get FireFox to send the
        # session cookie when navigating back from GitHub's login. (Tested
        # with FF 88)
        cookie["session_id"]["samesite"] = "lax"
        cookie["session_id"]["path"] = "/"

        return cookie.output(header="")

    @staticmethod
    async def authenticated(
        conn: Connection = Depends(Postgres.connection),
        session_id: t.Optional[str] = Cookie(None),
    ) -> Session:
        res = await Session.optional(conn, session_id)
        if isinstance(res, SessionProblem):
            raise res.as_http_exception()
        return res

    @staticmethod
    async def optional(
        conn: Connection = Depends(Postgres.connection),
        session_id: t.Optional[str] = Cookie(None),
    ) -> t.Union[SessionProblem, Session]:
        logger.info(f"Received cookie {session_id}")

        if session_id is None:
            return SessionProblem.MISSING

        try:
            session_id_uuid = uuid.UUID(hex=session_id)
        except ValueError:
            return SessionProblem.INVALID

        query = """
            SELECT user_id, created_at, expires_at, status FROM sessions
            WHERE session_id = $1 AND status = 'valid';"""

        row = await conn.fetchrow(query, session_id_uuid)

        if row is None:
            return SessionProblem.INVALID

        session = Session(**{"session_id": session_id_uuid, **dict(row)})

        now = datetime.datetime.now(datetime.timezone.utc)
        if session.expires_at <= now:
            return SessionProblem.EXPIRED

        return session
