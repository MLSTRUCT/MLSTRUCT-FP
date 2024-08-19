"""
MLSTRUCT-FP - UTILS - PATH

Path utils.
"""

__all__ = ['make_dirs']

import os


def make_dirs(f: str) -> str:
    """
    Create dir if not exists.

    :param f: Filename
    :returns: File
    """
    if f != '':
        fdir = os.path.dirname(f)
        os.makedirs(fdir, exist_ok=True)
    return f
