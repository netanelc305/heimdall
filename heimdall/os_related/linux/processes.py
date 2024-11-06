import logging
from functools import cached_property

from libvmi import LibvmiError

from heimdall.heimdall_client import HeimdallClient
from heimdall.os_related.base_os.processes import Process, Processes
from heimdall.os_related.linux.filesystem import LinuxFileSystem

logger = logging.getLogger(__name__)


class LinuxProcess(Process):
    """
    Represents a Linux process, providing access to process attributes such as name, PID, and path.
    """

    @cached_property
    def name(self) -> str:
        """
        The name of the process.

        Returns
        -------
        str
            The name of the process.
        """
        return self.ks.comm[0]

    @cached_property
    def pid(self) -> int:
        """
        The process ID (PID).

        Returns
        -------
        int
            The process ID.
        """
        return self.ks.pid[0]

    @cached_property
    def path(self) -> str:
        """
        The file path associated with the process executable.

        Returns
        -------
        str
            The full path of the executable file, or the process name if path retrieval fails.
        """
        try:
            return LinuxFileSystem.dentry_full_path(self.ks.mm[0].exe_file[0].f_path.dentry[0])
        except LibvmiError:
            return self.name


class LinuxProcesses(Processes):
    """
    Manages Linux processes, allowing listing of all processes in the system.
    """

    def __init__(self, heimdall_client: HeimdallClient):
        """
        Initialize the LinuxProcesses manager with a Heimdall client.

        Parameters
        ----------
        heimdall_client : HeimdallClient
            The client used for interacting with the system kernel.
        """
        super().__init__(heimdall_client)
        init_task = self.hc.kernel.symbols_jar.get_symbol('init_task')
        self.proc_list = self.hc.kernel.file_symbol(init_task.address, init_task.kind)

    def list(self) -> list[LinuxProcess]:
        """
        List all processes.

        Returns
        -------
        list of LinuxProcess
            A list of all Linux processes.
        """
        processes = []
        task_offset = self.hc.kernel.symbols_jar.get_type('task_struct').fields['tasks'].offset
        current_entry = self.proc_list.tasks.next[0]
        while True:
            current_proc = self.hc.kernel.symbol(current_entry.address - task_offset).cast('task_struct')
            processes.append(LinuxProcess(ks=current_proc, ctx=self.hc.create_ctx(current_proc.pid[0])))
            current_entry = current_entry.next[0]
            if current_entry == self.proc_list.tasks.next[0]:
                break
        return processes
