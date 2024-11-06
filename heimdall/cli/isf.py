import logging

import click

from heimdall.cli.cli_common import ISF_MANAGER, cb_kvmi_socket, prompt_selection
from heimdall.exceptions import SymbolsFileNotFoundError

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Entry point for the CLI."""
    pass


@cli.group()
def isf():
    """Group for ISF-related commands."""
    pass


def select_file(isf_files: dict, value: str = None) -> str:
    """Select an ISF file from the list or prompt the user."""
    if len(isf_files) == 0:
        raise SymbolsFileNotFoundError()
    if value is None:
        value = prompt_selection(list(isf_files.keys()), 'Select ISF file:')
    elif value not in isf_files:
        raise SymbolsFileNotFoundError()
    return isf_files[value]


def isf_callback(ctx, param, value):
    """Callback to select an ISF file."""
    isf_files = ISF_MANAGER.list()
    return select_file(isf_files, value)


@isf.command('list')
def isf_list():
    """List all available ISF files."""
    for isf_file in ISF_MANAGER.list():
        print(isf_file)


@isf.command('detect')
@click.argument('vm_name')
@click.option('--kvmi-socket', '-k', callback=cb_kvmi_socket, help='KVMI socket path')
def isf_detect(vm_name: str, kvmi_socket: dict[str, str]):
    """Detect an ISF file for a given VM name."""
    banner, banner_b64 = ISF_MANAGER.detect(vm_name, kvmi_socket)
    logger.info(banner)
    logger.info(f'Execute `heimdall isf download -b {banner_b64}` to download the ISF file')


@isf.command('purge')
def isf_purge():
    """Purge all ISF files."""
    ISF_MANAGER.purge()


@isf.command('delete')
@click.argument('name', callback=isf_callback, required=False)
def isf_delete(name: str):
    """Delete a specific ISF file."""
    ISF_MANAGER.delete(name)


@isf.command('create')
@click.argument('vm_name')
@click.option('--kvmi-socket', '-k', callback=cb_kvmi_socket, help='KVMI socket path')
def isf_create(vm_name: str, kvmi_socket):
    """Create an ISF file for a given VM name."""
    ISF_MANAGER.create(vm_name, kvmi_socket)


@isf.command('download')
@click.argument('out_path')
@click.option('banner', '-b', help='OS banner base64 encoded')
def isf_download(banner: str, out_path: str):
    """Download an ISF file using the OS banner."""
    ISF_MANAGER.download(banner, out_path)
