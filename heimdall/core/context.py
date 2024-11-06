import logging
from typing import Any, Optional

from heimdall.core.access import MemoryAccess
from heimdall.core.isf_file import ISFFile
from heimdall.core.symbol import Symbol
from heimdall.core.symbols_jar import SymbolsJar

logger = logging.getLogger(__name__)


class Context:
    """
    Represents the context in which Heimdall operates.

    The `Context` class provides access to memory and symbol information, managing
    the virtual machine's memory access, symbol profiles, and slide offsets.
    """

    def __init__(self, vm_access: MemoryAccess, dwarf: Optional[Any] = None, slide: int = 0):
        """Initialize the Context with memory access, optional symbols file, and slide offset.

        Parameters
        ----------
        vm_access : MemoryAccess
            The memory access object used to read and write memory.
        dwarf : Optional[Any], optional
            The path to the symbols file or an `ISFFile` object, by default None.
        slide : int, optional
            The slide offset to adjust addresses, by default 0.
        """
        self.vm_access = vm_access
        self.symbols_jar = None
        self.profile = None
        if dwarf:
            self.create_symbols_jar(dwarf)
        self.slide = slide

    def symbol(self, address: int, descriptor: Optional[Any] = None) -> Symbol:
        """Create a `Symbol` object based on the given address and descriptor.

        Parameters
        ----------
        address : int
            The memory address of the symbol.
        descriptor : Optional[Any], optional
            The type descriptor of the symbol, by default None.

        Returns
        -------
        Symbol
            The `Symbol` object representing the memory symbol.
        """
        return Symbol(self, address, descriptor)

    def file_symbol(self, address: int, descriptor: Optional[Any] = None) -> Symbol:
        """Create a `Symbol` object adjusted by the slide offset.

        Parameters
        ----------
        address : int
            The file-relative memory address of the symbol.
        descriptor : Optional[Any], optional
            The type descriptor of the symbol, by default None.

        Returns
        -------
        Symbol
            The `Symbol` object representing the memory symbol, adjusted for the slide.
        """
        if self.slide == 0:
            logger.warning("Using `file_symbol` when `slide == 0` may return incorrect address.")
        return self.symbol(address + self.slide, descriptor)

    def peek(self, address: int, size: int) -> bytes:
        """Read bytes from a given address in the process's memory.

        Parameters
        ----------
        address : int
            The memory address to read from.
        size : int
            The number of bytes to read.

        Returns
        -------
        bytes
            The bytes read from memory.
        """
        return self.vm_access.read(address, size)

    def peek_str(self, address: int) -> str:
        """Read a null-terminated string from a given address in the process's memory.

        Parameters
        ----------
        address : int
            The memory address to read the string from.

        Returns
        -------
        str
            The string read from memory.
        """
        return self.vm_access.read_str(address)

    def peek_ustr(self, address: int) -> str:
        return self.vm_access.read_ustr(address)

    def poke(self, address: int, data: bytes) -> None:
        """Write bytes to a given address in the process's memory.

        Parameters
        ----------
        address : int
            The memory address to write to.
        data : bytes
            The data to write.
        """
        return self.vm_access.write(address, data)

    def __repr__(self):
        return f'<Context({self.vm_access.pid})>'

    def create_symbols_jar(self, dwarf):
        self.symbols_jar = SymbolsJar(ISFFile(dwarf))
