import pytest
from sr_client import *


@pytest.fixture
def conn():
    return AqmSrClient()


def test_get_waves(conn):
    result = conn.get_waves("toronto")
    print("got waves for 'toronto' = " + repr(result))
    assert isinstance(result["valid_time"], str)
    assert isinstance(result["wave_height_ft"], int)
