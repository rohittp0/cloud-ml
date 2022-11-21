import subprocess

from config.variables import set_up

config = set_up()


def run():
    subprocess.Popen("python -m venv venv && "
                     ". venv/bin/activate && "
                     "pip install -r requirements.txt").wait()

    db = config["database"]

    subprocess.Popen("docker run --rm  --name  postgres "
                     f"-p {db['port']}:{db['port']} "
                     f"-e POSTGRES_USER={db['user']} "
                     f"-e POSTGRES_PASSWORD={db['password']} "
                     f"-e POSTGRES_DB={db['name']} "
                     f"-d postgres").wait()

    subprocess.Popen("alembic upgrade head").wait()


if __name__ == "__main__":
    run()
