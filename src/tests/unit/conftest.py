import pytest
import pds.api.run as run


@pytest.fixture
def flask_app():
    return run.get_app()
