from collections.abc import Mapping
from dataclasses import dataclass
from typing import Union


@dataclass(repr=False)
class Descriptor:
    """Base class representing a descriptor with a name."""
    name: str

    def __repr__(self) -> str:
        return f'{type(self).__name__}'


@dataclass
class KindDescriptor(Descriptor):
    """Represents a kind descriptor with a specific size."""
    size: int


@dataclass(repr=False)
class SymbolDescriptor(Descriptor):
    """Represents a symbol with an address and a kind of descriptor."""
    address: int
    kind: Descriptor

    def __repr__(self) -> str:
        return f'<{super().__repr__()}: {hex(self.address)}>'


@dataclass
class Field:
    """Represents a field in a complex type with an offset and type."""
    offset: int
    type: KindDescriptor


@dataclass(repr=False)
class BaseKind(KindDescriptor):
    """Base class for specific kinds of descriptors with a format."""
    fmt: str

    def __repr__(self) -> str:
        return f'<{super().__repr__()}: {self.name}>'


@dataclass
class ClassKind(BaseKind):
    """Represents a kind descriptor specifically for classes."""
    pass


@dataclass
class FunctionKind(BaseKind):
    """Represents a kind descriptor specifically for functions."""
    pass


@dataclass(repr=False)
class EnumKind(BaseKind):
    """Represents a kind descriptor for enums, including constants."""
    constants: dict[str, int]


@dataclass(repr=False)
class PointerKind(BaseKind):
    """Represents a kind descriptor for pointers, including a subtype."""
    subtype: KindDescriptor

    def __repr__(self) -> str:
        return f'<{super().__repr__()}: {getattr(self.subtype, "name", self.subtype)}*>'


@dataclass(repr=False)
class ArrayKind(KindDescriptor):
    """Represents a kind descriptor for arrays, including count and subtype."""
    count: int
    subtype: KindDescriptor


@dataclass(repr=False)
class ComplexKind(KindDescriptor):
    """Represents a composite kind descriptor with multiple fields."""
    fields: Mapping[str, Field]

    def __repr__(self) -> str:
        return f'<{super().__repr__()}: {self.name}>'


@dataclass(repr=False)
class StructKind(ComplexKind):
    """Represents a kind descriptor for structures."""
    pass


@dataclass(repr=False)
class UnionKind(ComplexKind):
    """Represents a kind descriptor for unions."""
    pass


@dataclass
class BitFieldKind(KindDescriptor):
    """Represents a bit field kind descriptor with bit length and position."""
    bit_length: int
    bit_position: int
    base_type: BaseKind


@dataclass
class UnresolvedKind(KindDescriptor):
    """Represents a kind descriptor for unresolved kinds with data."""
    data: Mapping


DescriptorType = Union[
    ComplexKind, PointerKind, ArrayKind, UnresolvedKind, BaseKind, SymbolDescriptor, FunctionKind, BitFieldKind]
