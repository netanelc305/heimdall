import logging
from functools import cached_property
from pathlib import Path

from libvmi import Libvmi

from heimdall.heimdall_client import HeimdallClient
from heimdall.os_related.windows.processes import WindowsProcesses

logger = logging.getLogger(__name__)


class WindowsClient(HeimdallClient):

    def __init__(self, vmi: Libvmi, profile: Path):
        """Initialize WindowsClient."""
        super().__init__(vmi, profile)
        self._processes = WindowsProcesses(self)

    @cached_property
    def kslide(self) -> int:
        """Return kernel slide value."""
        return self._vmi.translate_ksym2v('PsActiveProcessHead') - self.kernel.symbols_jar.symbols[
            'PsActiveProcessHead'].address

    @property
    def processes(self) -> WindowsProcesses:
        """Return Windows processes."""
        return self._processes

    @processes.setter
    def processes(self, procs: WindowsProcesses) -> None:
        """Set Windows processes."""
        self._processes = procs
