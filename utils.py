import shutil
import subprocess


def clone_repo(url):
    name = url.split("/")[-1].split(".")[0]
    shutil.rmtree(f"repos/{name}", ignore_errors=True)
    out = subprocess.check_output(["git", "clone", url, f"repos/{name}"])

    print(out)

    return name
