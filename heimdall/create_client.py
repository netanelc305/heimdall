from pathlib import Path

from libvmi import Libvmi

from heimdall.heimdall_client import HeimdallClient


def create_heimdall_client(vmi: Libvmi, profile: Path) -> HeimdallClient:
    """ Factory function to create a HeimdallClient for managing virtual machines. """
    return HeimdallClient(vmi, profile)
