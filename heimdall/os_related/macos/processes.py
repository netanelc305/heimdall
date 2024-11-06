import logging
from functools import cached_property

from heimdall.heimdall_client import HeimdallClient
from heimdall.os_related.base_os.processes import Process, Processes
from heimdall.os_related.macos.filesystem import MacOSFileSystem

logger = logging.getLogger(__name__)


class MacOSProcess(Process):
    """
    Represents a macOS process, providing access to attributes such as PID, name, and path.
    """

    @cached_property
    def pid(self) -> int:
        """
        Process ID (PID).

        Returns
        -------
        int
            The process ID.
        """
        return self.ks.p_pid[0]

    @cached_property
    def name(self) -> str:
        """
        Process name.

        Returns
        -------
        str
            The name of the process.
        """
        return self.ks.p_comm[0]

    @cached_property
    def path(self) -> str:
        """
        Process path.

        Returns
        -------
        str
            The full path of the process executable.
        """
        return MacOSFileSystem.vnode_full_path(self.ks.p_textvp[0])


class MacOSProcesses(Processes):
    """
    Manages a collection of macOS processes, providing methods to retrieve processes by various attributes.
    """

    def __init__(self, heimdall_client: HeimdallClient):
        """
        Initialize the MacOSProcesses manager with a Heimdall client.

        Parameters
        ----------
        heimdall_client : HeimdallClient
            The client used for interacting with the system kernel.
        """
        super().__init__(heimdall_client)
        allproc_symbol = self.hc.kernel.symbols_jar.get_symbol('allproc')
        self.proc_list = self.hc.kernel.file_symbol(allproc_symbol.address, allproc_symbol.kind)

    def list(self) -> list[MacOSProcess]:
        """
        List all processes.

        Returns
        -------
        list of MacOSProcess
            A list of all macOS processes.
        """
        processes = []
        current_proc = self.proc_list.lh_first[0]
        while True:
            pid = current_proc.p_pid[0]
            processes.append(MacOSProcess(ks=current_proc, ctx=self.hc.create_ctx(pid)))
            if pid == 0:
                break
            current_proc = current_proc.p_list.le_next[0]
        return processes
