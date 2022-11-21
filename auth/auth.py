from datetime import timedelta

from fastapi import HTTPException, APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from google.auth.exceptions import GoogleAuthError
from sqlalchemy.ext.asyncio import AsyncSession

from starlette.responses import JSONResponse, RedirectResponse
from starlette.requests import Request

from google.oauth2 import id_token
from google.auth.transport import requests
from starlette.templating import Jinja2Templates

from auth.dependencies import create_access_token, get_user_by_email, create_user
from auth.models import Token
from config.db import get_db
from config.variables import set_up

config = set_up()
templates = Jinja2Templates(directory="auth/templates")

COOKIE_AUTHORIZATION_NAME = "Authorization"

API_LOCATION = f"{config['protocol']}{config['domain']}:{config['port']}"
SWAP_TOKEN_ENDPOINT = "/auth/swap_token"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()


@router.get("/auth/login_google", tags=["security"])
def google_login_client(request: Request, next_page="/"):
    context = {
        "client_id": config['google']['id'],
        "api_location": API_LOCATION,
        "swap_token_endpoint": SWAP_TOKEN_ENDPOINT,
        "success_route": next_page,
        "app_name": config['name'],
        "request": request
    }
    return templates.TemplateResponse("login.html", context=context)


@router.post(f"{SWAP_TOKEN_ENDPOINT}", response_model=Token, tags=["security"])
async def swap_token(request: Request, db: AsyncSession = Depends(get_db)):
    if not request.headers.get("X-Requested-With"):
        raise HTTPException(status_code=400, detail="Incorrect headers")

    body_bytes = await request.body()
    auth_code = jsonable_encoder(body_bytes)

    try:
        info = id_token.verify_oauth2_token(auth_code, requests.Request(), config["google"]["id"])

        print(info)

        if info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        if info['email'] and info['email_verified']:
            email = info.get('email')

        else:
            raise HTTPException(status_code=400, detail="Unable to validate social login")

    except GoogleAuthError:
        raise HTTPException(status_code=400, detail="Unable to validate social login")

    if not await get_user_by_email(email, db):
        await create_user(email, info.get("name"), -1, info.get("picture"), db)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )

    token = jsonable_encoder(access_token)

    response = JSONResponse({"access_token": token, "token_type": "bearer"})

    response.set_cookie(
        COOKIE_AUTHORIZATION_NAME,
        value=f"Bearer {token}",
        domain=config["domain"],
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response


@router.get("/auth/logout")
async def route_logout_and_remove_cookie(next_page="/"):
    response = RedirectResponse(url=next_page)
    response.delete_cookie("Authorization", domain=config["domain"])

    return response
