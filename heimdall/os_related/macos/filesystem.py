from collections.abc import Iterator
from typing import Any

from heimdall.core.symbol import Symbol


class MacOSFileSystem:
    """ Provides utilities for interacting with the macOS file system, specifically for vnode operations. """

    @staticmethod
    def vnode_traversal(v_node: Symbol) -> Iterator[Any]:
        """Traverse the vnode hierarchy starting from a given vnode.

        Parameters
        ----------
        v_node : Symbol
            The vnode from which to start traversal.

        Yields
        ------
        Symbol
            Each vnode in the hierarchy from the given vnode up to the root.
        """
        v_node_iter = v_node
        while v_node_iter != 0:
            yield v_node_iter
            v_node_iter = v_node_iter.v_parent[0]

    @staticmethod
    def vnode_full_path(v_node: Symbol) -> str:
        """Return the full path of a vnode by traversing its parent hierarchy.

        Parameters
        ----------
        v_node : Symbol
            The vnode for which to retrieve the full path.

        Returns
        -------
        str
            The full path of the vnode.
        """
        path = []
        for v in MacOSFileSystem.vnode_traversal(v_node):
            path.append(v.v_name[0])
        ret = '/' + '/'.join(path[::-1])
        return ret
