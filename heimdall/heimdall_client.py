import logging
import sys
from abc import abstractmethod
from functools import cached_property
from pathlib import Path
from typing import Any, Optional

import IPython
from humanfriendly.terminal.html import html_to_ansi
from IPython.terminal.prompts import Prompts, Token
from libvmi import Libvmi
from traitlets.config import Config

from heimdall.core.access import MemoryAccess
from heimdall.core.context import Context

BANNER = """
<b>Heimdall has been successfully loaded! 😎
Usage:
 <span style="color: magenta">h</span>   Global to access heimdall features.
 <span style="color: magenta">k</span>   Global to access kernel context.

Have a nice flight ✈️! Starting an IPython shell...
"""

logger = logging.getLogger(__name__)


class ContextPrompt(Prompts):
    """ Customizes IPython prompts in the Heimdall context. """

    def in_prompt_tokens(self, cli: Optional[Any] = None) -> list[tuple[Token, str]]:
        return [(Token.Prompt, 'Heimdall:> ')]

    def out_prompt_tokens(self, cli: Optional[Any] = None) -> list[tuple[Token, str]]:
        return [(Token.Prompt, 'Heimdall:> ')]


class HeimdallClient:
    def __init__(self, vmi: Libvmi, os_profile: Path):
        """
        Represents a client for interacting with the Heimdall virtual machine introspection library.

        The `HeimdallClient` class provides methods for initializing the client using a virtual
        machine name and an OS profile. It supports reading and writing memory, creating contexts
        for specific processes, and starting an IPython interactive shell for advanced interactions.

        Parameters
        ----------
        vmi : Libvmi
            The Libvmi instance for interacting with the VM.
        os_profile : Path
            The path to the OS profile configuration file.
        """
        self.profile = os_profile
        self._vmi = vmi
        self.kernel = Context(MemoryAccess(self._vmi, 0), os_profile)
        self.kernel.slide = self.kslide
        self._current_context = self.kernel

    @property
    @abstractmethod
    def processes(self):
        """Abstract property for processes."""
        pass

    @processes.setter
    def processes(self, value):
        """
        Setter for the processes' property.

        Parameters
        ----------
        value : Any
            The value to set for processes.
        """
        pass

    @cached_property
    @abstractmethod
    def kslide(self) -> int:
        """
        Kernel slide.

        Returns
        -------
        int
            The kernel ASLR slide value.
        """
        pass

    def create_ctx(self, pid: int, symbols_path: str = None) -> Context:
        """
        Create a context for a given PID.

        Parameters
        ----------
        pid : int
            The process ID for which to create the context.
        symbols_path : str, optional
            The path to the symbols file (default is None).

        Returns
        -------
        Context
            A context object for the specified PID.
        """
        return Context(MemoryAccess(self._vmi, pid), symbols_path)

    def interact(self, additional_namespace: Optional[dict] = None) -> None:
        """
        Start an IPython interactive shell.

        Parameters
        ----------
        additional_namespace : dict, optional
            Additional variables to include in the interactive namespace (default is None).
        """
        ipython_config = self._create_ipython_config()
        sys.argv = ['a']
        IPython.start_ipython(
            config=ipython_config,
            user_ns={'h': self, 'k': self.kernel, **(additional_namespace or {})}
        )

    @staticmethod
    def _create_ipython_config() -> Config:
        """
        Create IPython configuration.

        Returns
        -------
        Config
            The IPython configuration for the interactive shell.
        """
        ipython_config = Config()
        ipython_config.IPCompleter.use_jedi = True
        ipython_config.BaseIPythonApplication.profile = 'heimdall'
        ipython_config.TerminalInteractiveShell.prompts_class = ContextPrompt
        ipython_config.InteractiveShellApp.exec_lines = [
            '''import logging;logging.getLogger('asyncio').disabled = True'''
        ]
        ipython_config.TerminalInteractiveShell.banner1 = html_to_ansi(BANNER)
        return ipython_config
