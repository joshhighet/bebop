import pytest
from app import cryptocurrency
from app import getpage

@pytest.fixture
def detail_to_group_basic():
    return {
        "address": "bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6",
    }

def test_walletexplorer(detail_to_group_basic):
    walletid, pivoted_address = cryptocurrency.walletexplorer_inspect_and_pivot(detail_to_group_basic["address"])
    assert len(pivoted_address) == 0 and walletid
