from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Callable, Optional

from capstone import CsInsn

from heimdall.core.context import Context
from heimdall.core.symbol import Symbol
from heimdall.heimdall_client import HeimdallClient
from heimdall.os_related.base_os.kernel_struct import KernelStruct


class Process(KernelStruct):
    """
    Abstract base class representing a process.

    This class provides an interface for interacting with processes, including methods
    to access process attributes and perform memory operations. Subclasses should implement
    the abstract methods to provide platform-specific functionality.

    Notes
    -----
    This is an interface class and should be subclassed. Subclasses must implement
    the abstract properties `pid`, `name`, and `path`.

    Examples
    --------
    Subclassing the Process class:

    >>> class MyProcess(Process):
    ...     @cached_property
    ...     def pid(self) -> int:
    ...         # Implement get process pid
    ...
    ...     @cached_property
    ...     def name(self) -> str:
    ...         # Implement get process name
    ...
    ...     @cached_property
    ...     def path(self) -> str:
    ...         # Implement get process path
    """

    def __init__(self, ks: Any, ctx: Context) -> None:
        """
        Initialize the Process.

        Parameters
        ----------
        ks : KernelStruct
            The kernel structure representing the process.
        ctx : Context
            The context associated with the process.
        """
        super().__init__(ks)
        self.ctx = ctx

    @cached_property
    @abstractmethod
    def pid(self) -> int:
        """Abstract property to return the process ID."""
        pass

    @cached_property
    @abstractmethod
    def name(self) -> str:
        """Abstract property to return the process name."""
        pass

    @cached_property
    @abstractmethod
    def path(self) -> str:
        """Abstract property to return the process path."""
        pass

    def slide(self) -> int:
        """
        Return the ASLR (Address Space Layout Randomization) value.

        Returns
        -------
        int
            The ASLR slide value.
        """
        return self.ctx.slide

    def peek(self, address: int, size: int) -> bytes:
        """
        Peek into memory at a specified address and retrieve a specified number of bytes.

        Parameters
        ----------
        address : int
            The memory address to peek at.
        size : int
            The number of bytes to read from the specified address.

        Returns
        -------
        bytes
            The bytes read from memory.
        """
        return self.symbol(address).peek(size)

    def peek_str(self, address: int) -> str:
        """
        Peek into memory at a specified address and retrieve a string.

        Parameters
        ----------
        address : int
            The memory address to peek at.

        Returns
        -------
        str
            The string read from memory.
        """
        return self.symbol(address).peek_str()

    def peek_ustr(self, address: int) -> str:
        """
        Peek into memory at a specified address and retrieve a Unicode string.

        Parameters
        ----------
        address : int
            The memory address to peek at.

        Returns
        -------
        str
            The Unicode string read from memory.
        """
        return self.symbol(address).peek_ustr()

    def poke(self, address: int, data: bytes) -> None:
        """
        Write data to memory at a specified address.

        Parameters
        ----------
        address : int
            The memory address to write to.
        data : bytes
            The data to write to the specified address.
        """
        return self.symbol(address).poke(data)

    def disass(self, address: int, size: int = 40) -> list[CsInsn]:
        """
        Disassemble a number of bytes starting from a specified address.

        Parameters
        ----------
        address : int
            The memory address to start disassembling from.
        size : int, optional
            The number of bytes to disassemble (default is 40).

        Returns
        -------
        list of CsInsn
            A list of disassembled instructions.
        """
        return self.symbol(address).disass(size)

    def symbol(self, address: int, descriptor: Optional[Any] = None) -> Symbol:
        """
        Retrieve a symbol at a specified address.

        Parameters
        ----------
        address : int
            The memory address of the symbol.
        descriptor : Optional[Any], optional
            Additional descriptor information for the symbol (default is None).

        Returns
        -------
        Symbol
            The symbol at the specified address.
        """
        return self.ctx.symbol(address, descriptor)

    def file_symbol(self, address: int, descriptor: Optional[Any] = None) -> Symbol:
        """
        Retrieve a file symbol at a specified address.

        Parameters
        ----------
        address : int
            The memory address of the file symbol.
        descriptor : Optional[Any], optional
            Additional descriptor information for the file symbol (default is None).

        Returns
        -------
        Symbol
            The file symbol at the specified address.
        """
        return self.ctx.file_symbol(address, descriptor)

    def __repr__(self) -> str:
        """
        Return a string representation of the process.

        Returns
        -------
        str
            The string representation of the process.
        """
        return f'<{self.__class__.__name__} PID:{self.pid} PATH:{self.path}>'


class Processes(ABC):
    """
    Abstract base class for managing processes.

    This class provides an interface for listing processes and retrieving processes
    by name or PID. Subclasses should implement the abstract methods to provide
    platform-specific functionality.

    Examples
    --------
    Subclassing the Processes class:

    >>> class MyProcesses(Processes):
    ...     def list(self) -> list[Process]:
    ...         # Implement process listing
    ...         pass
    ...
    ...     def get_by_name(self, name: str) -> Optional[Process]:
    ...         # Implement retrieval by name
    ...         pass
    ...
    ...     def get_by_pid(self, pid: int) -> Optional[Process]:
    ...         # Implement retrieval by PID
    ...         pass
    """

    def __init__(self, hc: HeimdallClient) -> None:
        """
        Initialize the Processes manager.

        Parameters
        ----------
        hc : HeimdallClient
            The Heimdall client used for interacting with the system.
        """
        self.hc = hc
        self.proc_list: Optional[list[Process]] = None

    @abstractmethod
    def list(self) -> list[Process]:
        """
        List all processes.

        Returns
        -------
        list of Process
            A list of all processes.
        """
        pass

    def get_by_name(self, process_name: str) -> Optional[Process]:
        """
        Get a process by name.

        Parameters
        ----------
        process_name : str
            The name of the process to retrieve.

        Returns
        -------
        Optional[Process]
            The process with the specified name, or None if not found.
        """
        return self._find_process(lambda p: p.name == process_name)

    def get_by_pid(self, process_id: int) -> Optional[Process]:
        """
        Get a process by PID.

        Parameters
        ----------
        process_id : int
            The PID of the process to retrieve.

        Returns
        -------
        Optional[Process]
            The process with the specified PID, or None if not found.
        """
        return self._find_process(lambda p: p.pid == process_id)

    def _find_process(self, condition: Callable[[Process], bool]) -> Optional[Process]:
        """
        Find a process that matches a specified condition.

        Parameters
        ----------
        condition : Callable[[Process], bool]
            A callable that defines the condition to match.

        Returns
        -------
        Optional[Process]
            The process that matches the condition, or None if not found.
        """
        for process in self.list():
            if condition(process):
                return process
        return None
