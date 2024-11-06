from typing import Any, Iterator

from heimdall.core.symbol import Symbol


class LinuxFileSystem:
    """
    Provides utilities for interacting with the Linux file system, specifically for dentry operations.
    """

    @staticmethod
    def dentry_traversal(dentry: Symbol) -> Iterator[Any]:
        """
        Traverse the dentry hierarchy starting from a given dentry.

        Parameters
        ----------
        dentry : Symbol
            The dentry from which to start traversal.

        Yields
        ------
        Symbol
            Each dentry in the hierarchy from the given dentry up to the root.
        """
        dentry_iter = dentry
        while dentry_iter and dentry_iter != dentry_iter.d_parent[0]:
            yield dentry_iter
            dentry_iter = dentry_iter.d_parent[0]

    @staticmethod
    def dentry_full_path(dentry: Symbol) -> str:
        """
        Return the full path of a dentry by traversing its parent hierarchy.

        Parameters
        ----------
        dentry : Symbol
            The dentry for which to retrieve the full path.

        Returns
        -------
        str
            The full path of the dentry.
        """
        path = []
        for d in LinuxFileSystem.dentry_traversal(dentry):
            name = d.d_name.name[0]
            path.append(name.decode() if isinstance(name, bytes) else name)
        # Reverse the path to construct the full path from root to the target dentry
        full_path = '/' + '/'.join(reversed(path))
        return full_path
