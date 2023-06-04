from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from auth import auth
from config.variables import set_up
from utils import clone_repo

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


@app.get("/clone")
def clone(url: str):
    name = clone_repo(url)

    return {
        "message": f"Repo cloned",
        "name": name
    }


@app.get("/run")
def run(name: str):
    pass
