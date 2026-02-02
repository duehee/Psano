# app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

user = os.getenv("DB_USER")
passwd = os.getenv("DB_PASSWD")
host = os.getenv("DB_HOST", "127.0.0.1")
port = os.getenv("DB_PORT", "3306")
db = os.getenv("DB_NAME")

DB_URL = f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8mb4"

engine = create_engine(
    DB_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,  # 1시간 후 연결 재사용 (stale connection 방지)
    pool_timeout=10,    # 풀에서 연결 대기 최대 시간
    connect_args={
        "connect_timeout": 10,  # DB 연결 타임아웃 (초)
        "read_timeout": 30,     # 읽기 타임아웃 (초)
        "write_timeout": 30,    # 쓰기 타임아웃 (초)
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()