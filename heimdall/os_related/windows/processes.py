import logging
from functools import cached_property

from libvmi import LibvmiError

from heimdall.heimdall_client import HeimdallClient
from heimdall.os_related.base_os.processes import Process, Processes

logger = logging.getLogger(__name__)


class WindowsProcess(Process):
    """
    Represents a Windows process, providing access to attributes such as PID, name, and path.
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
        return self.ks.UniqueProcessId.cast('unsigned int')[0]

    @cached_property
    def name(self) -> str:
        """
        Process name.

        Returns
        -------
        str
            The name of the process.
        """
        return self.ks.ImageFileName[0]

    @cached_property
    def path(self) -> str:
        """
        Process path.

        Returns
        -------
        str
            The full path of the process executable, or the process name if path retrieval fails.
        """
        try:
            res = self.ks.ImageFilePointer[0].FileName[0]
        except LibvmiError:
            res = self.name
        return res


class WindowsProcesses(Processes):
    """
    Manages a collection of Windows processes, providing methods to retrieve processes by various attributes.
    """

    def __init__(self, heimdall_client: HeimdallClient):
        """
        Initialize the WindowsProcesses manager with a Heimdall client.

        Parameters
        ----------
        heimdall_client : HeimdallClient
            The client used for interacting with the system kernel.
        """
        super().__init__(heimdall_client)
        ps_active_process_head = self.hc.kernel.symbols_jar.get_symbol('PsActiveProcessHead')
        self.proc_list = self.hc.kernel.file_symbol(
            ps_active_process_head.address).cast('_LIST_ENTRY')

    def list(self) -> list[WindowsProcess]:
        """
        List all processes.

        Returns
        -------
        list of WindowsProcess
            A list of all Windows processes.
        """
        processes = []
        task_offset = self.hc.kernel.symbols_jar.get_type('_EPROCESS').fields['ActiveProcessLinks'].offset
        current_entry = self.proc_list.Flink[0]
        while True:
            current_proc = self.hc.kernel.symbol(current_entry.address - task_offset).cast('_EPROCESS')
            pid = current_proc.UniqueProcessId.cast('unsigned int')[0]
            processes.append(WindowsProcess(ks=current_proc, ctx=self.hc.create_ctx(pid)))
            if current_entry == self.proc_list:
                break
            current_entry = current_proc.ActiveProcessLinks.Flink[0]
        return processes
