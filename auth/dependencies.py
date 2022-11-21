from typing import Optional
from datetime import timedelta, datetime

import jwt
from jwt import PyJWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.status import HTTP_403_FORBIDDEN

from fastapi import HTTPException, Depends
from fastapi.security.oauth2 import OAuth2, OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param

from config.db import get_db
from auth.models import User
from config.variables import set_up

config = set_up()


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
            self,
            token_url: str,
            scheme_name: str = None,
            scopes: dict = None,
            auto_error: bool = False,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False
            scheme = ""
            param = None

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None

        return param


oauth2_scheme = OAuth2PasswordBearerCookie(token_url="/token")


async def get_user_by_email(email: str, db: AsyncSession):
    query = select(User).where(User.email == email)
    users = await db.execute(query)

    return users.first()


async def create_user(email: str, name: str, phone: int, picture: str, db: AsyncSession):
    user = User(email=email, name=name, phone=phone, picture=picture)
    db.add(user)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config["secret"], algorithm="HS256")
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, config["secret"], algorithms=["HS256"])
        email: str = payload.get("sub")

        if email is None:
            return None

    except PyJWTError:
        return None

    user = await get_user_by_email(email=email, db=db)

    if user is None:
        return None

    return user


def login_redirect(current: str):
    return RedirectResponse(f"/auth/login_google?next_page={current}", status_code=307)


# class BasicAuth(SecurityBase):
#     def __init__(self, scheme_name: str = None, auto_error: bool = True):
#         self.scheme_name = scheme_name or self.__class__.__name__
#         self.auto_error = auto_error
#
#     async def __call__(self, request: Request) -> Optional[str]:
#         authorization: str = request.headers.get("Authorization")
#         scheme, param = get_authorization_scheme_param(authorization)
#         if not authorization or scheme.lower() != "basic":
#             if self.auto_error:
#                 raise HTTPException(
#                     status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
#                 )
#             else:
#                 return None
#         return param
#
#
# basic_auth = BasicAuth(auto_error=False)
