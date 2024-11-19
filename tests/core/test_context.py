import pytest

from heimdall.core.symbol import Symbol
from heimdall.heimdall_client import HeimdallClient


@pytest.mark.parametrize('file_address', [18446744071616658624])
def test_file_symbol(heimdall_client: HeimdallClient, file_address: int) -> None:
    """
    Test to verify that the file symbol is correctly retrieved and is of the type `Symbol`.

    Parameters
    ----------
    heimdall_client : HeimdallClient
        The Heimdall client used to retrieve the file symbol.
    file_address : int
        The address of the file to retrieve the symbol from.

    Returns
    -------
    None
    """
    init_task = heimdall_client.kernel.file_symbol(file_address)
    assert isinstance(init_task, Symbol)
    assert init_task == heimdall_client.kernel.slide + file_address
