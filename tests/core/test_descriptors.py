import pytest

from heimdall.core.descriptors import ArrayKind, BaseKind, ComplexKind, EnumKind, Field, PointerKind, StructKind
from heimdall.core.symbols_jar import SymbolsJar


@pytest.mark.parametrize('name,size,num_of_fields', [
    ('task_struct', 13696, 268),
    ('tcp_ao_key', 168, 17),
    ('bpf_dynptr', 16, 1),
    ('acpi_operand_object', 72, 26),
])
def test_complex_kind(symbols_jar: SymbolsJar, name: str, size: int, num_of_fields: int) -> None:
    """
    Verify ComplexKind descriptor.

    Parameters
    ----------
    symbols_jar : SymbolsJar
        The SymbolsJar used to retrieve the type descriptor.
    name : str
        The name of the complex type.
    size : int
        The expected size of the complex type.
    num_of_fields : int
        The expected number of fields in the complex type.

    Returns
    -------
    None
    """
    complex_descriptor = symbols_jar.get_type(name)
    assert issubclass(complex_descriptor.__class__, ComplexKind)
    assert complex_descriptor.name == name
    assert complex_descriptor.size == size
    assert len(complex_descriptor.fields) == num_of_fields


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
def test_complex_fields(symbols_jar: SymbolsJar, name: str, offset: int, kind: type) -> None:
    """
    Verify ComplexKind Fields.

    Parameters
    ----------
    symbols_jar : SymbolsJar
        The SymbolsJar used to retrieve the type descriptor.
    name : str
        The name of the field.
    offset : int
        The expected offset of the field.
    kind : type
        The expected kind of the field.

    Returns
    -------
    None
    """
    complex_descriptor = symbols_jar.get_type('task_struct')
    field = complex_descriptor.fields[name]
    assert isinstance(field, Field)
    assert isinstance(field.type, kind)
    assert field.offset == offset


@pytest.mark.parametrize('name,size,fmt', [
    ('_Bool', 1, '?'),
    ('__int128', 16, 'qq'),
    ('__int128 unsigned', 16, 'QQ'),
    ('double', 8, 'd'),
    ('float', 4, 'f'),
    ('int', 4, 'i'),
    ('long int', 8, 'q'),
    ('long long int', 8, 'q'),
    ('long long unsigned int', 8, 'Q'),
    ('long unsigned int', 8, 'Q'),
    ('pointer', 8, 'Q'),
    ('short int', 2, 'h'),
    ('short unsigned int', 2, 'H'),
    ('signed char', 1, 'b'),
    ('ssizetype', 8, 'q'),
    ('unsigned char', 1, 'B'),
    ('unsigned int', 4, 'I'),
    ('void', 0, 'P')
])
def test_base_kind(symbols_jar: SymbolsJar, name: str, size: int, fmt: str) -> None:
    """
    Verify BaseKind descriptor.

    Parameters
    ----------
    symbols_jar : SymbolsJar
        The SymbolsJar used to retrieve the type descriptor.
    name : str
        The name of the basic type.
    size : int
        The expected size of the basic type.
    fmt : str
        The expected format of the basic type.

    Returns
    -------
    None
    """
    _type = symbols_jar.get_type(name)
    assert _type.name == name
    assert _type.size == size
    assert _type.fmt == fmt


def test_pointer_kind(symbols_jar: SymbolsJar) -> None:
    """
    Verify PointerKind descriptor.

    Parameters
    ----------
    symbols_jar : SymbolsJar
        The SymbolsJar used to retrieve the type descriptor.

    Returns
    -------
    None
    """
    summary_lock_data = symbols_jar.get_type('summary_lock_data')
    new_contended_rdev = summary_lock_data.fields['new_contended_rdev'].type
    assert isinstance(new_contended_rdev, PointerKind)
    assert isinstance(new_contended_rdev.subtype, PointerKind)
    assert isinstance(new_contended_rdev.subtype.subtype, StructKind)


@pytest.mark.parametrize(
    'name,size,constants', [
        ('HV_GENERIC_SET_FORMAT', 4, {'HV_GENERIC_SET_ALL': 1, 'HV_GENERIC_SET_SPARSE_4K': 0}),
        ('KTHREAD_BITS', 4, {'KTHREAD_IS_PER_CPU': 0, 'KTHREAD_SHOULD_PARK': 2, 'KTHREAD_SHOULD_STOP': 1})
    ]
)
def test_enum_kind(symbols_jar: SymbolsJar, name: str, size: int, constants: dict) -> None:
    """
    Verify EnumKind descriptor.

    Parameters
    ----------
    symbols_jar : SymbolsJar
        The SymbolsJar used to retrieve the type descriptor.
    name : str
        The name of the enum type.
    size : int
        The expected size of the enum type.
    constants : dict
        The expected constants of the enum type.

    Returns
    -------
    None
    """
    enum_descriptor = symbols_jar.get_enum(name)
    assert isinstance(enum_descriptor, EnumKind)
    assert enum_descriptor.size == size
    assert enum_descriptor.constants == constants


def test_array_kind(symbols_jar: SymbolsJar) -> None:
    """
    Verify ArrayKind descriptor.

    Parameters
    ----------
    symbols_jar : SymbolsJar
        The SymbolsJar used to retrieve the symbol.

    Returns
    -------
    None
    """
    array_descriptor = symbols_jar.get_symbol('xstate_sizes').kind
    assert isinstance(array_descriptor, ArrayKind)
    assert array_descriptor.count == 19
    assert array_descriptor.size == array_descriptor.subtype.size * array_descriptor.count
