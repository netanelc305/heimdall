import logging
import struct
from dataclasses import dataclass
from typing import Optional, Union

from capstone import CS_ARCH_X86, CS_MODE_64, CS_MODE_LITTLE_ENDIAN, Cs, CsInsn

from heimdall.core.descriptors import ArrayKind, BaseKind, BitFieldKind, ComplexKind, DescriptorType, PointerKind, \
    UnresolvedKind

logger = logging.getLogger(__name__)


@dataclass(repr=False)
class Symbol:
    """
    Represents a memory-resident symbol with associated type information, providing methods
    for reading and writing values from memory.

    The `Symbol` class acts as an abstraction for symbols in memory, offering type-aware
    memory access and manipulation. It supports handling complex types, arrays, pointers,
    and bitfields.


    Notes
    -----
    The class uses `__getitem__` and `__setitem__` to handle reading from and writing to
    memory based on the type descriptor:

    This simplifies interaction with memory by providing type-safe, structured access
    to memory addresses.

    Examples
    --------
    Accessing an array element or dereferencing a pointer:

    .. code-block:: python

        symbol = Symbol(ctx, address, descriptor)
        value = symbol[0]      # Access an array element or dereference a pointer.
        symbol[0] = 42         # Write a value to memory.
    """

    def __init__(self, ctx: 'Context', address: int, descriptor: Optional[DescriptorType] = None):  # noqa: F821
        """
        Parameters
        ----------
        ctx : Context
            The context object managing memory access and symbol resolution.
        address : int
            The memory address where the symbol is located.
        descriptor : Optional[DescriptorType]
            The type descriptor associated with the symbol, determining how the memory should be interpreted.
        """
        self.ctx = ctx
        self.address = address
        self.descriptor = descriptor

    def cast(self, type_name: str) -> 'Symbol':
        """
        Cast the symbol to another type.

        Parameters
        ----------
        type_name : str
            The name of the type to cast the symbol to.

        Returns
        -------
        Symbol
            A new Symbol instance cast to the specified type.
        """
        return Symbol(self.ctx, self.address, self.ctx.symbols_jar.get_type(type_name))

    def peek(self, size: int) -> bytes:
        """
        Peek into memory at the symbol's address and retrieve a specified number of bytes.

        Parameters
        ----------
        size : int
            The number of bytes to read from the symbol's address.

        Returns
        -------
        bytes
            The bytes read from memory.
        """
        return self.ctx.peek(self.address, size)

    def peek_str(self) -> str:
        """
        Peek into memory at the symbol's address and retrieve a string.

        Returns
        -------
        str
            The string read from memory.
        """
        return self.ctx.peek_str(self.address)

    def poke(self, data: bytes) -> None:
        """
        Write data to memory at the symbol's address.

        Parameters
        ----------
        data : bytes
            The data to write to the symbol's address.
        """
        return self.ctx.poke(self.address, data)

    def peek_ustr(self) -> str:
        """
        Peek into memory at the symbol's address and retrieve a Unicode string.

        Returns
        -------
        str
            The Unicode string read from memory.
        """
        return self.ctx.peek_str(self.address)

    def disass(self, size: int = 40) -> list[CsInsn]:
        """
        Disassemble a number of bytes starting from the symbol's address.

        Parameters
        ----------
        size : int, optional
            The number of bytes to disassemble (default is 40).

        Returns
        -------
        list of CsInsn
            A list of disassembled instructions.
        """
        return list(Cs(CS_ARCH_X86, CS_MODE_LITTLE_ENDIAN | CS_MODE_64).disasm(self.peek(size), int(self)))

    def __repr__(self) -> str:
        """Return string representation of the symbol."""
        dec = '' if self.descriptor is None else f'p ({self.descriptor.name}*)'
        return f'<{self.__class__.__name__}({self.ctx.vm_access.pid}): {dec}{hex(self.address)}>'

    def __int__(self) -> int:
        """Return the address as an integer."""
        return self.address

    def __eq__(self, other: int) -> bool:
        """Check equality based on the address."""
        return self.address == other

    def __add__(self, other: int) -> 'Symbol':
        """Check equality based on the address."""
        return Symbol(self.ctx, self.address + other)

    def __sub__(self, other: int) -> 'Symbol':
        """Check equality based on the address."""
        return Symbol(self.ctx, self.address - other)

    def __dir__(self) -> list:
        """List all attributes and fields."""
        ret = list(self.__dict__.keys())
        if self.descriptor and isinstance(self.descriptor, ComplexKind):
            ret.extend(list(self.descriptor.fields.keys()))
        return ret

    def __getattr__(self, name: str) -> 'Symbol':
        """Get attribute by name."""
        if self.descriptor and isinstance(self.descriptor, ComplexKind):
            try:
                field = self.descriptor.fields[name]
                return self.ctx.symbol(self.address + field.offset, field.type)
            except KeyError:
                pass
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __getitem__(self, idx: int) -> Optional[Union[int, str, tuple, 'Symbol']]:
        """Get item by index."""
        if isinstance(self.descriptor, ComplexKind):
            if self.descriptor.name == '_UNICODE_STRING':
                return self.ctx.vm_access.read_ustr(self.address + idx * self.descriptor.size)
            logger.warning('Unable to dereference complex type')
            return None
        elif isinstance(self.descriptor, ArrayKind):
            return self._handle_array_kind(idx)
        elif isinstance(self.descriptor, PointerKind):
            return self._handle_pointer_kind(idx)
        elif isinstance(self.descriptor, BitFieldKind):
            return self._handle_bitfield(idx)
        fmt, size = self.descriptor.fmt, self.descriptor.size
        data = self.ctx.vm_access.read(self.address + idx * size, size)
        result = struct.unpack(fmt, data)[0]
        return result

    def __setitem__(self, idx: int, value: Union[int, str, tuple]) -> None:
        """Set item by index."""
        if not self.descriptor or isinstance(self.descriptor, ComplexKind):
            logger.warning('Unable to dereference complex type')
            return None
        elif isinstance(self.descriptor, ArrayKind):
            self._handle_array_kind_set(idx, value)
        elif isinstance(self.descriptor, PointerKind):
            self._handle_pointer_kind_set(idx, value)
        elif isinstance(self.descriptor, BitFieldKind):
            self._handle_bitfield_set(idx, value)
        else:
            fmt, size = self.descriptor.fmt, self.descriptor.size
            data = struct.pack(fmt, value)
            self.ctx.vm_access.write(self.address + idx * size, data)

    def _handle_array_kind(self, idx: int) -> Union[str, tuple]:
        """Handle array kind."""
        if self.descriptor.subtype.name in ['char', 'unsigned char']:
            ret = self.ctx.vm_access.read_str(self.address + idx * self.descriptor.size)
        else:
            if isinstance(self.descriptor.subtype, BaseKind):
                data = self.ctx.vm_access.read(self.address + idx * self.descriptor.subtype.size, self.descriptor.size)
                ret = struct.unpack(self.descriptor.count * self.descriptor.subtype.fmt, data)
            else:
                ret = self.ctx.symbol(self.address + idx * self.descriptor.subtype.size, self.descriptor.subtype)
        return ret

    def _handle_array_kind_set(self, idx: int, value: Union[str, tuple]) -> None:
        """Handle setting array kind."""
        if self.descriptor.subtype.name in ['char', 'unsigned char']:
            self.ctx.vm_access.write_str(self.address + idx * self.descriptor.size, value)
        else:
            data = struct.pack(self.descriptor.count * self.descriptor.subtype.fmt, *value)
            self.ctx.vm_access.write(self.address + idx * self.descriptor.size, data)

    def _handle_pointer_kind(self, idx: int) -> 'Symbol':
        """Handle pointer kind."""
        subtype = self.descriptor.subtype
        if isinstance(subtype, UnresolvedKind):
            type_name = subtype.data['name']
            subtype = self.ctx.symbols_jar.get_type(type_name)
        fmt, size = self.descriptor.fmt, self.descriptor.size
        data = self.ctx.vm_access.read(self.address + idx * size, size)
        ptr_result = struct.unpack(fmt, data)[0]
        if subtype.name in ['char', 'unsigned char']:
            ret = self.ctx.vm_access.read_str(ptr_result)
        else:
            ret = self.ctx.symbol(ptr_result, subtype)
        return ret

    def _handle_pointer_kind_set(self, idx: int, value: int) -> None:
        """Handle setting pointer kind."""
        fmt, size = self.descriptor.fmt, self.descriptor.size
        data = struct.pack(fmt, int(value))
        self.ctx.vm_access.write(self.address + idx * size, data)

    def _handle_bitfield(self, idx: int) -> int:
        """Handle bitfield kind."""
        fmt, size = self.descriptor.base_type.fmt, self.descriptor.base_type.size
        data = self.ctx.vm_access.read(self.address + idx * size, size)
        unpacked = struct.unpack(fmt, data)[0]
        return 1 << self.descriptor.bit_position & unpacked

    def _handle_bitfield_set(self, idx: int, value: int) -> None:
        """Handle setting bitfield kind."""
        fmt, size = self.descriptor.base_type.fmt, self.descriptor.base_type.size
        data = self.ctx.vm_access.read(self.address + idx * size, size)
        unpacked = struct.unpack(fmt, data)[0]
        bit_mask = 1 << self.descriptor.bit_position
        if value != 0:
            new_value = unpacked | bit_mask
        else:
            new_value = unpacked & ~bit_mask
        new_data = struct.pack(fmt, new_value)
        self.ctx.vm_access.write(self.address + idx * size, new_data)
