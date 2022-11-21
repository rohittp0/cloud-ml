from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from auth import auth
from auth.dependencies import get_current_user, login_redirect
from auth.models import User
from config.variables import set_up

app = FastAPI()
config = set_up()

origins = [
    f"{config['protocol']}{config['domain']}",
    f"{config['protocol']}{config['domain']}:{config['port']}"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

if config['debug']:
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home(current_user: User = Depends(get_current_user)):
    if not current_user:
        return login_redirect("/")

    return current_user
