import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    # Für jeden Test eine frische, leere Datenbank in einem temporären Ordner
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    with app.test_client() as client:
        yield client
