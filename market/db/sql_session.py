from configparser import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

config = ConfigParser()
config.read("database.conf")
config = config["DEFAULT"]

user = config["POSTGRES_USER"]
password = config["POSTGRES_PASSWORD"]
host = config["POSTGRES_HOST"] + ":" + config["POSTGRES_PORT"]
database_name = config["POSTGRES_DB"]

engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@{host}/{database_name}"
)
engine.connect()

Session = sessionmaker(bind=engine)
session = Session()
session._model_changes = {}

