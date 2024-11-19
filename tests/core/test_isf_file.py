import pytest

from heimdall.core.isf_file import ISFFile, OSType


@pytest.mark.parametrize('_type,expected', [
    ('int', {'size': 4, 'signed': True, 'kind': 'int', 'endian': 'little'}),  # base_type
    ('IO_APIC_reg_00', {'size': 4, 'fields': {  # user_type
        'bits': {'type': {'kind': 'struct', 'name': 'unnamed_fbeb7bdcbe9725ea'}, 'offset': 0},
        'raw': {'type': {'kind': 'base', 'name': 'unsigned int'}, 'offset': 0}},
                        'kind': 'union'})
])
def test_get_type(isf_file: ISFFile, _type: str, expected: dict) -> None:
    """
    Verify `get_type` functionality.

    Parameters
    ----------
    isf_file : ISFFile
        Our ISFFile instance containing type information.
    _type : str
        The type name we are looking up.
    expected : dict
        What we expect `get_type` to return.

    Returns
    -------
    None
    """
    assert isf_file.get_type(_type) == expected


@pytest.mark.parametrize('symbol,expected', [
    ('init_task', {'type': {'kind': 'struct', 'name': 'task_struct'}, 'address': 18446744071616658624}),
    ('scsi_eh_bus_device_reset', {'type': {'kind': 'base', 'name': 'void'}, 'address': 18446744071591435552})
])
def test_get_symbol(isf_file: ISFFile, symbol: str, expected: dict) -> None:
    """
    Verify `get_symbol` functionality.

    Parameters
    ----------
    isf_file : ISFFile
        Our ISFFile instance containing symbol information.
    symbol : str
        The symbol name we are looking up.
    expected : dict
        The expected result from `get_symbol`.

    Returns
    -------
    None
    """
    assert isf_file.get_symbol(symbol) == expected


@pytest.mark.parametrize('_enum,expected', [
    ('HV_GENERIC_SET_FORMAT', {'size': 4, 'base': 'unsigned int',
                               'constants': {'HV_GENERIC_SET_ALL': 1, 'HV_GENERIC_SET_SPARSE_4K': 0}})
])
def test_get_enum(isf_file: ISFFile, _enum: str, expected: dict) -> None:
    """
    Verify `get_enum` functionality.

    Parameters
    ----------
    isf_file : ISFFile
        Our ISFFile instance containing enum information.
    _enum : str
        The enum name we are investigating.
    expected : dict
        The expected data from `get_enum`.

    Returns
    -------
    None
    """
    assert isf_file.get_enum(_enum) == expected


def test_get_os_type(isf_file: ISFFile) -> None:
    """
    Verify `get_os_type` functionality.

    Parameters
    ----------
    isf_file : ISFFile
        Our ISFFile instance containing OS information.

    Returns
    -------
    None
    """
    assert isf_file.get_os_type() == OSType.LINUX
