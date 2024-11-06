import click
from libvmi import INIT_DOMAINNAME, Libvmi, LibvmiError, VMIConfig

from heimdall.cli.cli_common import cb_isf, cb_kvmi_socket, sudo_required
from heimdall.create_client import create_heimdall_client
from heimdall.exceptions import ConnectionFailedError


@click.group()
def cli() -> None:
    """Main CLI group for Heimdall commands."""
    pass


@cli.command('connect')
@click.argument('vm_name')
@click.option('--isf', '-i', callback=cb_isf, help='Path to ISF file')
@click.option('--kvmi-socket', callback=cb_kvmi_socket, help='KVMI socket path')
@sudo_required
def cli_connect(vm_name: str, isf: str, kvmi_socket: dict[str, str]) -> None:
    """Connect to a virtual machine with Heimdall."""
    try:
        vmi = Libvmi(
            vm_name,
            INIT_DOMAINNAME,
            config_mode=VMIConfig.JSON_PATH,
            config=str(isf),
            partial=False,
            init_data=kvmi_socket
        )
    except LibvmiError:
        raise ConnectionFailedError()
    else:
        hc = create_heimdall_client(vmi, isf)
        hc.interact()
        vmi.destroy()
