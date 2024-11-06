import logging
from functools import cached_property
from pathlib import Path

from libvmi import Libvmi

from heimdall.heimdall_client import HeimdallClient
from heimdall.os_related.linux.processes import LinuxProcesses

logger = logging.getLogger(__name__)


class LinuxClient(HeimdallClient):

    def __init__(self, vmi: Libvmi, profile: Path):
        """Initialize LinuxClient."""
        super().__init__(vmi, profile)
        self._processes = LinuxProcesses(self)

    @cached_property
    def kslide(self) -> int:
        """Return kernel slide value."""
        return self._vmi.translate_ksym2v('init_task') - self.kernel.symbols_jar.symbols[
            'init_task'].address

    @property
    def processes(self) -> LinuxProcesses:
        """Return Linux processes."""
        return self._processes

    @processes.setter
    def processes(self, procs: LinuxProcesses) -> None:
        """Set Linux processes."""
        self._processes = procs
