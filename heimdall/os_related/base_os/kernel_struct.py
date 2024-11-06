from dataclasses import dataclass

from heimdall.core.symbol import Symbol


@dataclass
class KernelStruct:
    """
    Represents a kernel structure in memory.

    .. warning::

        The `ks` parameter represents the real kernel structure in memory. Accessing or modifying it directly,
        such as by setting ``ks.p_pid[0] = 9999`` (assuming `ks` is of type `proc*`), will override the **real PID**
        in the virtual machine and can cause crashes. **Use it only if you know what you're doing.**

    Parameters
    ----------
    ks : Symbol
        The symbol representing the kernel structure.
    """

    ks: Symbol
