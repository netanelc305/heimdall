import pytest

from heimdall.core.descriptors import ArrayKind, BaseKind, PointerKind, StructKind
from heimdall.core.symbol import Symbol

TEST_SIZE = 4


@pytest.mark.parametrize('_type,expected', [('int', BaseKind),
                                            ('pointer', BaseKind),
                                            ('task_struct', StructKind)])
def test_cast(systemd_symbol, _type: str, expected: type) -> None:
    """
    Verify cast operation returns a Symbol with the expected descriptor type.

    Parameters
    ----------
    systemd_symbol : Symbol
        The symbol to be cast.
    _type : str
        The type to cast the symbol to.
    expected : type
        The expected descriptor type.

    Returns
    -------
    None
    """
    casted = systemd_symbol.cast(_type)
    assert isinstance(casted, Symbol)
    assert isinstance(casted.descriptor, expected)


def test_peek(systemd_symbol: Symbol) -> None:
    """
    Verify peek operation returns the expected byte sequence.

    Parameters
    ----------
    systemd_symbol : Symbol
        The symbol to peek.

    Returns
    -------
    None
    """
    assert systemd_symbol.peek(TEST_SIZE) == b'\x02\x00\x00\x00'


def test_peek_str(systemd_symbol: Symbol) -> None:
    """
    Verify peek_str operation returns the expected string.

    Parameters
    ----------
    systemd_symbol : Symbol
        The symbol to peek as string.

    Returns
    -------
    None
    """
    casted = systemd_symbol.cast('task_struct')
    assert casted.comm.peek_str() == 'systemd'


def test_disass(systemd_symbol: Symbol) -> None:
    """
    Verify disass operation returns a non-empty result.

    Parameters
    ----------
    systemd_symbol : Symbol
        The symbol to disassemble.

    Returns
    -------
    None
    """
    assert len(systemd_symbol.disass(TEST_SIZE)) > 0


@pytest.mark.parametrize('name, offset, kind', [
    ('__state', 24, BaseKind),
    ('acct_rss_mem1', 3464, BaseKind),
    ('active_mm', 2344, PointerKind),
    ('btrace_seq', 1032, BaseKind),
    ('cg_list', 3640, StructKind),
    ('comm', 3008, ArrayKind),
    ('fs', 3072, PointerKind),
    ('pid', 2464, BaseKind),
    ('task_works', 3192, PointerKind),
    ('usage', 40, StructKind)
])
def test_get_attr(systemd_symbol: Symbol, name: str, offset: int, kind: type) -> None:
    """
    Verify __getattr__ returns a Symbol with the expected descriptor type and address offset.

    Parameters
    ----------
    systemd_symbol : Symbol
        The symbol to get attribute from.
    name : str
        The attribute name to get.
    offset : int
        The expected offset of the attribute.
    kind : type
        The expected descriptor type.

    Returns
    -------
    None
    """
    casted = systemd_symbol.cast('task_struct')
    attr = casted.__getattr__(name)
    assert isinstance(attr, Symbol)
    assert isinstance(attr.descriptor, kind)
    assert attr.address == casted.address + offset


@pytest.mark.parametrize('name, expected', [
    ('comm', 'systemd'),
    ('pid', 1),
    ('frozen', 0),
    ('latency_record', StructKind),
])
def test_getitem(systemd_symbol: Symbol, name: str, expected: any) -> None:
    """
    Verify __getitem__ returns the expected value or descriptor type.

    Parameters
    ----------
    systemd_symbol : Symbol
        The symbol to get item from.
    name : str
        The item name to get.
    expected : any
        The expected value or descriptor type.

    Returns
    -------
    None
    """
    attr = systemd_symbol.cast('task_struct').__getattr__(name)[0]
    if isinstance(attr, Symbol):
        assert isinstance(attr.descriptor, expected)
    else:
        assert attr == expected
