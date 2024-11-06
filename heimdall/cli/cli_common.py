import functools
import os
from pathlib import Path
from typing import Any, Callable, Union

import click
import inquirer3
from inquirer3.themes import GreenPassion
from libvmi import VMIInitData

from heimdall.cli.isf_manager import ISFManager
from heimdall.exceptions import AccessDeniedError, SymbolsFileNotFoundError

ISF_MANAGER = ISFManager(Path(str(click.get_app_dir('heimdall'))) / 'isf_files')


def cb_isf(ctx: click.Context, param: click.Parameter, value: Union[str, None]) -> Union[Path, None]:
    """Retrieve ISF path from provided value, or from ISF manager based on VM name in context."""
    if value is not None:
        return Path(value)
    else:
        try:
            vm_name: str = ctx.params.get('vm_name')
            symbols_file: Path = ISF_MANAGER.list()[vm_name]
            return symbols_file
        except KeyError:
            raise SymbolsFileNotFoundError()


def cb_kvmi_socket(ctx: click.Context, param: click.Parameter, value: Union[str, None]) -> Union[dict[str, str], None]:
    """Return a dictionary with KVMI_SOCKET key if value is provided, else None."""
    return {VMIInitData.KVMI_SOCKET: value} if value else None


def sudo_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to ensure the function is run with root permissions."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        if not os.geteuid() == 0:
            raise AccessDeniedError()
        else:
            func(*args, **kwargs)

    return wrapper


def prompt_selection(choices: list[str], prompt_message: str, return_index: bool = False) -> Union[str, int, None]:
    """Prompt the user to select from a list of choices. Returns the choice or its index if specified."""
    question = [inquirer3.List('selection', message=prompt_message, choices=choices, carousel=True)]
    try:
        result = inquirer3.prompt(question, theme=GreenPassion(), raise_keyboard_interrupt=True)
    except KeyboardInterrupt:
        raise click.ClickException('No selection was made')
    return result['selection'] if not return_index else choices.index(result['selection'])
