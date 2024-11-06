from libvmi import Libvmi


class MemoryAccess:
    """
    Provides methods for accessing and manipulating memory using Libvmi.

    The `MemoryAccess` class allows reading and writing to a virtual machine's memory space
    by utilizing the Libvmi library. It supports operations such as reading bytes, writing bytes,
    reading strings, and writing strings to specific memory addresses within a process.
    """

    def __init__(self, vmi: Libvmi, pid: int):
        """Initialize the MemoryAccess with a Libvmi instance and PID.

        Parameters
        ----------
        vmi : Libvmi
            An instance of the Libvmi library initialized for the target virtual machine.
        pid : int
            The process ID (PID) of the target process within the virtual machine.
        """
        self.vmi = vmi
        self.pid = pid

    def write(self, address: int, data: bytes) -> None:
        """Write bytes to a specific memory address.

        Parameters
        ----------
        address : int
            The memory address to write data to.
        data : bytes
            The bytes data to write to memory.
        """
        self.vmi.write_va(address, self.pid, data)

    def read(self, address: int, size: int) -> bytes:
        """Read bytes from a specific memory address.

        Parameters
        ----------
        address : int
            The memory address to read data from.
        size : int
            The number of bytes to read.

        Returns
        -------
        bytes
            The bytes read from memory.
        """
        return self.vmi.read_va(address, self.pid, size)[0]

    def read_str(self, address: int) -> str:
        """Read a null-terminated string from a specific memory address.

        Parameters
        ----------
        address : int
            The memory address to read the string from.

        Returns
        -------
        str
            The string read from memory.
        """
        return self.vmi.read_str_va(address, self.pid)

    def read_ustr(self, address: int) -> str:
        """Read a null-terminated string from a specific memory address.

        Parameters
        ----------
        address : int
            The memory address to read the string from.

        Returns
        -------
        str
            The string read from memory.
        """
        return self.vmi.read_unicode_str_va(address, self.pid)

    def write_str(self, address: int, data: str) -> None:
        """Write a string to a specific memory address (with null termination).

        Parameters
        ----------
        address : int
            The memory address to write the string to.
        data : str
            The string data to write to memory.
        """
        data = data.encode() + b'\x00'
        self.write(address, data)
