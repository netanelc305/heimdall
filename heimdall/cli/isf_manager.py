import base64
import json
import logging
import lzma
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import requests
from libvmi import Libvmi, LibvmiError

from heimdall.exceptions import SymbolsFileNotFoundError, SymbolsFileRemoteNotFoundError
from heimdall.utils.utils import download_file

logger = logging.getLogger(__name__)
MAC_AND_LINUX_REPO = 'https://raw.githubusercontent.com/Abyss-W4tcher/volatility3-symbols/master/banners/banners.json'
CHUNK_SIZE = 0x200000
MACOS_BANNER_SIGNATURE = b'Darwin Kernel Version'
LINUX_BANNER_SIGNATURE = b'Linux version'


class ISFManager:
    """Manager class for handling ISF profiles."""

    def __init__(self, profiles_directory: Path) -> None:
        """
        Initialize ISFManager with the provided profile's directory.

        Parameters
        ----------
        profiles_directory : Path
            The directory where ISF profiles are stored.
        """
        self.profiles_directory = profiles_directory

    def list(self) -> dict[str, Path]:
        """
        List all available ISF profiles.

        Returns
        -------
        dict of str : Path
            A dictionary mapping profile names to their file paths.

        Raises
        ------
        SymbolsFileNotFoundError
            If the profiles directory does not exist.
        """
        profiles = {}
        if not self.profiles_directory.exists():
            raise SymbolsFileNotFoundError()
        for profile_file in self.profiles_directory.iterdir():
            profiles[profile_file.stem] = profile_file
        return profiles

    def delete(self, profile_name: str) -> None:
        """
        Delete a specific ISF profile.

        Parameters
        ----------
        profile_name : str
            The name of the profile to delete.

        Raises
        ------
        FileExistsError
            If the specified profile does not exist.
        """
        profile_path = Path(self.profiles_directory / profile_name).with_suffix('.json')
        if not profile_path.exists():
            raise FileExistsError()
        profile_path.unlink()
        logger.info(f'Deleted: {profile_name}')

    def purge(self) -> None:
        """
        Purge all ISF profiles.

        Deletes all profiles found in the profiles directory.
        """
        for profile_name, profile_path in self.list().items():
            self.delete(profile_name)
        logger.info(f'Deleted all profiles in: {self.profiles_directory}')

    @staticmethod
    def detect(vm_name: str, kvmi_socket: dict) -> Optional[Tuple[str, str]]:
        """
        Detect the kernel signature of a VM.

        Parameters
        ----------
        vm_name : str
            The name of the virtual machine.
        kvmi_socket : dict
            KVMI socket data for communication with the VM.

        Returns
        -------
        tuple of (str, str) or None
            A tuple containing the decoded banner and its base64-encoded version, or None if detection fails.
        """
        logger.info(f'Scanning for kernel signature: {MACOS_BANNER_SIGNATURE} | {LINUX_BANNER_SIGNATURE}')
        with Libvmi(vm_name, init_data=kvmi_socket, partial=True) as vmi:
            max_physical_address = vmi.get_max_physical_address()
            for address in range(0, max_physical_address, CHUNK_SIZE):
                if banner := ISFManager._read_banner(vmi, address):
                    return banner.decode('utf-8'), base64.b64encode(banner).decode()
        logger.error('Unable to determine OS')
        return None

    @staticmethod
    def _read_banner(vmi: Libvmi, address: int) -> Optional[bytes]:
        """
        Read the kernel banner from memory.

        Parameters
        ----------
        vmi : Libvmi
            The Libvmi instance for interacting with VM memory.
        address : int
            The memory address to start reading from.

        Returns
        -------
        bytes or None
            The kernel banner as bytes, or None if the banner cannot be read.
        """
        try:
            data = vmi.read_pa(address, CHUNK_SIZE)[0]
            if MACOS_BANNER_SIGNATURE in data:
                banner = data[data.index(MACOS_BANNER_SIGNATURE):].split(b'\x00', 1)[0] + b'\x00\n'
                return banner
            elif LINUX_BANNER_SIGNATURE in data:
                banner = data[data.index(LINUX_BANNER_SIGNATURE):].split(b'\n', 1)[0] + b'\x00\n'
                return banner
        except LibvmiError:
            pass
        return None

    @staticmethod
    def _extract(source: str, dest: str) -> None:
        """
        Extract JSON data from a xz compressed file.

        Parameters
        ----------
        source : str
            Path to the xz compressed source file.
        dest : str
            Path to the destination file for extracted JSON data.
        """
        with lzma.open(source) as xz:
            data = json.load(xz)
        with open(dest, 'w') as dest_file:
            json.dump(data, dest_file)

    def download(self, banner: str, outfile: str) -> None:
        """
        Download and extract an ISF profile.

        Parameters
        ----------
        banner : str
            Base64-encoded OS banner to identify the ISF file.
        outfile : str
            Name for the downloaded ISF file.

        Raises
        ------
        SymbolsFileRemoteNotFoundError
            If the banner is not found in the repository.
        """
        banners = requests.get(MAC_AND_LINUX_REPO).json()
        if banner in banners['mac']:
            download_url = banners['mac'][banner][0]
        elif banner in banners['linux']:
            download_url = banners['linux'][banner][0]
        else:
            raise SymbolsFileRemoteNotFoundError(banner)
        filename = os.path.basename(download_url)
        outfile_path = self.profiles_directory / f'{outfile}.json'
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            xz_file = tmpdir_path / filename
            self.profiles_directory.mkdir(exist_ok=True, parents=True)
            download_file(download_url, xz_file)
            logger.info('Extracting symbols file (may take a while)...')
            self._extract(xz_file, outfile_path)
            logger.info(f'Symbols file is now available {outfile_path}')

    def create(self, vm_name: str, kvmi_socket: dict) -> None:
        """
        Create an ISF profile for a specified VM.

        Parameters
        ----------
        vm_name : str
            The name of the virtual machine.
        kvmi_socket : dict
            KVMI socket data for communication with the VM.
        """
        result = self.detect(vm_name, kvmi_socket)
        if result:
            banner, banner_b64 = result
            self.download(banner_b64, vm_name)
        else:
            logger.error('Profile creation failed due to detection failure.')
