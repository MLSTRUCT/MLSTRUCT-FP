"""
MLSTRUCTFP - UTILS - PATH

Path utils.
"""

__all__ = ['make_dirs']

import os


def make_dirs(f: str) -> None:
    """
    Create dir if not exists.

    :param f: Filename
    """
    fdir = os.path.dirname(f)
    if f != '':
        os.makedirs(fdir, exist_ok=True)
