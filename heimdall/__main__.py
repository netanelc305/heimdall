import logging

import click
import coloredlogs

from heimdall.cli.connect import cli as cli_connect
from heimdall.cli.isf import cli as cli_profiles
from heimdall.exceptions import AccessDeniedError, ConnectionFailedError, SymbolsFileNotFoundError, \
    SymbolsFileRemoteNotFoundError

logging.getLogger('urllib3.connectionpool').disabled = True

coloredlogs.install(level=logging.DEBUG)


def cli():
    cli_commands = click.CommandCollection(sources=[cli_profiles, cli_connect])
    cli_commands.context_settings = dict(help_option_names=['-h', '--help'])
    try:
        cli_commands()
    except SymbolsFileNotFoundError as e:
        logging.error(f'Symbols file not found. Use `heimdall isf create {e.name if e.name != "" else "VM_NAME"}`')
    except SymbolsFileRemoteNotFoundError:
        logging.error('Symbols file not found on remote repository. You should create it manually - '
                      'https://volatility3.readthedocs.io/en/latest/symbol-tables.html')
    except AccessDeniedError:
        logging.error('Permissions error. Try again using sudo')
    except ConnectionFailedError:
        logging.error('Unable to connect verify vm is running and run heimdall as sudo')


if __name__ == '__main__':
    cli()
