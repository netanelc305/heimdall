import pytest

from heimdall.core.descriptors import BaseKind, EnumKind, StructKind, UnionKind


@pytest.mark.parametrize('name,kind', [
    ('int', BaseKind),
    ('task_struct', StructKind),
    ('IO_APIC_reg_00', UnionKind),
])
def test_get_type(symbols_jar, name: str, kind: type) -> None:
    """
    Verify get_type returns the correct kind.

    Parameters
    ----------
    symbols_jar : SymbolsJar
        The SymbolsJar instance holding type information.
    name : str
        The name of the type to be verified.
    kind : type
        The expected kind of the type.

    Returns
    -------
    None
    """
    assert isinstance(symbols_jar.get_type(name), kind)


@pytest.mark.parametrize('name,type_name,address', [
    ('init_task', 'task_struct', 18446744071616658624),
])
def test_get_symbol(symbols_jar, name: str, type_name: str, address: int) -> None:
    """
    Verify get_symbol returns a symbol with the correct type and address.

    Parameters
    ----------
    symbols_jar : SymbolsJar
        The SymbolsJar instance holding symbol information.
    name : str
        The name of the symbol to be verified.
    type_name : str
        The expected type name of the symbol.
    address : int
        The expected address of the symbol.

    Returns
    -------
    None
    """
    sym = symbols_jar.get_symbol(name)
    assert sym.kind == symbols_jar.get_type(type_name)
    assert sym.address == address


@pytest.mark.parametrize('name', ['HV_GENERIC_SET_FORMAT'])
def test_get_enum(symbols_jar, name: str) -> None:
    """
    Verify get_enum returns the correct EnumKind.

    Parameters
    ----------
    symbols_jar : SymbolsJar
        The SymbolsJar instance holding enum information.
    name : str
        The name of the enum to be verified.

    Returns
    -------
    None
    """
    assert isinstance(symbols_jar.get_enum(name), EnumKind)
