"""
MLSTRUCTFP - UTILS - PLOT - GENERIC

Generic plot abstract class.
"""

__all__ = ['GenericPlot']

from abc import ABC, abstractmethod
import plotly.graph_objects as go


class GenericPlot(ABC):
    """
    Generic plotting class.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        ABC.__init__(self)

    @abstractmethod
    def basic(self) -> 'go.Figure':
        """
        Basic plot.

        :return: Go figure object
        """
        pass

    @abstractmethod
    def complex(self) -> 'go.Figure':
        """
        Complex plot.

        :return: Go figure object
        """
        pass
