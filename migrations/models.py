from config.db import Base
import auth.models


def get_metadata():
    return Base.metadata
