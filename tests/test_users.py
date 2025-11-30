from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import db_manager
from app.main import app

# 1. 创建一个独立的内存 SQLite 数据库引擎
TEST_DATABASE_URL = "sqlite:///./test.db" # 或者使用 "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
# 2. 创建测试会话工厂
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)
# 3. 定义测试专用的依赖项
def override_get_db():
    """这个函数会取代 db_manager 作为依赖项"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# 4. 应用依赖项覆盖
# 告诉 FastAPI，每当有人请求 db_manager 依赖项时，使用 override_get_db
app.dependency_overrides[db_manager] = override_get_db

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users/",
        json={
            "name": "testuser",
            "email": "syang2501@outlook.com",
            "password": "123.qwe",
            "mobile": "17649862173"
        }
    )
    print(f'{response}')
    assert response is not None
    assert response.status_code == 200
    assert response.json()["name"] == "testuser"
