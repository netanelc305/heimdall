import logging
from functools import cached_property
from pathlib import Path

from libvmi import Libvmi

from heimdall.heimdall_client import HeimdallClient
from heimdall.os_related.macos.processes import MacOSProcesses

logger = logging.getLogger(__name__)


class MacOSClient(HeimdallClient):

    def __init__(self, vmi: Libvmi, profile: Path):
        """Initialize MacOSClient."""
        super().__init__(vmi, profile)
        self._processes = MacOSProcesses(self)

    @cached_property
    def kslide(self) -> int:
        """Return kernel slide value."""
        return self._vmi.translate_ksym2v('allproc') - self.kernel.symbols_jar.symbols[
            'allproc'].address

    @property
    def processes(self) -> MacOSProcesses:
        """Return MacOS processes."""
        return self._processes

    @processes.setter
    def processes(self, procs: MacOSProcesses) -> None:
        """Set MacOS processes."""
        self._processes = procs
