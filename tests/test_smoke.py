from app.core.config import get_settings
from app.core.database import Base
from app.models.documento import Documento
from app.models.trd_ccd import TRDEntry
from app.models.expediente import Expediente


def test_config_loads():
    settings = get_settings()
    assert settings.app_name
    assert settings.database_url


def test_models_registered():
    tables = Base.metadata.tables
    assert Documento.__tablename__ in tables
    assert TRDEntry.__tablename__ in tables
    assert Expediente.__tablename__ in tables
