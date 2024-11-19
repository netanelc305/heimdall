from pathlib import Path
from typing import Any, Generator

import pytest
from libvmi import Libvmi, VMIConfig

from heimdall.core.isf_file import ISFFile
from heimdall.core.symbols_jar import SymbolsJar
from heimdall.create_client import create_heimdall_client

TEST_FILES = Path(__file__).resolve().parent / 'test_files'
ISF_FILE_PATH = TEST_FILES / 'isf_files' / 'linux.json'
MEM_DUMP = TEST_FILES / 'memory_dumps' / 'ubuntu.mem'
SYSTEMD_ADDRESS = 0xffff916540348000


@pytest.fixture(scope='module')
def heimdall_client() -> Generator[Any, None, None]:
    """
    Fixture to create a Heimdall client for use in tests.

    Yields
    ------
    Any
        The Heimdall client.
    """
    with Libvmi(str(MEM_DUMP), config=str(ISF_FILE_PATH), config_mode=VMIConfig.JSON_PATH) as vmi:
        yield create_heimdall_client(vmi, ISF_FILE_PATH)


@pytest.fixture(scope='module')
def symbols_jar(isf_file: ISFFile) -> SymbolsJar:
    """
    Fixture to create a SymbolsJar for use in tests.

    Parameters
    ----------
    isf_file : ISFFile
        The ISF file to use for creating the SymbolsJar.

    Returns
    -------
    SymbolsJar
        The SymbolsJar object.
    """
    return SymbolsJar(isf_file)


@pytest.fixture(scope='module')
def isf_file() -> ISFFile:
    """
    Fixture to create an ISFFile for use in tests.

    Returns
    -------
    ISFFile
        The ISFFile object.
    """
    return ISFFile(ISF_FILE_PATH)


@pytest.fixture(scope='function')
def systemd_symbol(heimdall_client: Any) -> Any:
    """
    Fixture to get the systemd symbol for use in tests.

    Parameters
    ----------
    heimdall_client : Any
        The Heimdall client used to retrieve the systemd symbol.

    Returns
    -------
    Any
        The systemd symbol.
    """
    return heimdall_client.kernel.symbol(SYSTEMD_ADDRESS)
