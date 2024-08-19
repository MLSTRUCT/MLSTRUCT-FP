"""
MLSTRUCT-FP - UTILS - PLOT

Plotting utils.
"""

__all__ = [
    'configure_figure',
    'DEFAULT_PLOT_DPI',
    'DEFAULT_PLOT_FIGSIZE',
    'DEFAULT_PLOT_STYLE',
    'save_figure'
]

import matplotlib as mpl
import matplotlib.pyplot as plt

# Some constants
DEFAULT_PLOT_DPI: int = 250
DEFAULT_PLOT_FIGSIZE: int = 6
DEFAULT_PLOT_STYLE: str = 'default'  # https://matplotlib.org/3.1.1/gallery/style_sheets/style_sheets_reference.html


def configure_figure(**kwargs) -> None:
    """
    Configure current figure.

    Optional parameters:
        cfg_dpi                 DPI settings
        cfg_equal_axis          Use equal axis
        cfg_fontsize_label      Label fontsize
        cfg_fontsize_ticks      Ticks fontsize
        cfg_fontsize_title      Title fontsize
        cfg_grid                Use grid
        cfg_tight_layout        Use tight layout
        cfg_xticks_rotation     Rotation of xticks
        cfg_yticks_rotation     Rotation of yticks

    :param kwargs: Optional keyword arguments
    """
    ax: 'plt.Axes' = plt.gca()
    f_lbl = kwargs.get('cfg_fontsize_label', 14)
    f_tik = kwargs.get('cfg_fontsize_ticks', 14)
    ax.yaxis.label.set_size(40)

    # Configure label size
    ax.xaxis.label.set_size(f_lbl)
    ax.yaxis.label.set_size(f_lbl)

    # Configure ticks size
    plt.xticks(fontsize=f_tik)
    plt.yticks(fontsize=f_tik)

    # Configure grid
    if kwargs.get('cfg_grid', True):
        plt.grid(True)

    # Configure title fontsize
    ax.title.set_fontsize(kwargs.get('cfg_fontsize_title', 14))

    if kwargs.get('cfg_tight_layout', False):
        plt.tight_layout()

    # mpl.rcParams['figure.dpi'] = kwargs.get('cfg_dpi', DEFAULT_PLOT_DPI)

    # Set current style
    plt.style.use(DEFAULT_PLOT_STYLE)

    # Rotate ticks
    rot_xticks = kwargs.get('cfg_xticks_rotation', 0)
    rot_yticks = kwargs.get('cfg_yticks_rotation', 0)
    if rot_xticks != 0:
        plt.xticks(rotation=rot_xticks)
    if rot_yticks != 0:
        plt.xticks(rotation=rot_yticks)

    if kwargs.get('cfg_equal_axis', False):
        plt.axis('square')


def save_figure(save: str, **kwargs) -> None:
    """
    Save figure to file if specified.

    Optional params:
        save_dpi            DPI image
        save_tight          Save plot with tight margins

    :param save: Savename
    :param kwargs: Optional keyword arguments
    """
    if save == '':
        return

    # Increases chunksize for larger plots
    mpl.rcParams['agg.path.chunksize'] = 100000

    dpi = kwargs.get('save_dpi', 3 * DEFAULT_PLOT_DPI)
    if kwargs.get('save_tight', True):
        plt.savefig(save, bbox_inches='tight', pad_inches=0.05, dpi=dpi)
    else:
        plt.savefig(save, dpi=dpi)
