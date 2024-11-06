from pathlib import Path

from libvmi import Libvmi

from heimdall.core.isf_file import ISFFile, OSType
from heimdall.heimdall_client import HeimdallClient
from heimdall.os_related.linux.linux_client import LinuxClient
from heimdall.os_related.macos.macos_client import MacOSClient


def create_heimdall_client(vmi: Libvmi, profile: Path) -> HeimdallClient:
    """ Factory function to create a HeimdallClient for managing virtual machines. """
    isf_file = ISFFile(profile)
    clients = {OSType.MACOS: MacOSClient, OSType.LINUX: LinuxClient}
    return clients.get(isf_file.get_os_type(), HeimdallClient)(vmi, profile)
