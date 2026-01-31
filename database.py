from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker 


DATABASE_URL = "postgresql://postgres:postgres@localhost/escola"

# Força UTF-8 na conexão (evita UnicodeDecodeError no Windows com locale PT-BR)
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c client_encoding=UTF8"},
)
SessionLocal = sessionmaker(bind=engine)


Base = declarative_base()