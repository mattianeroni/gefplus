from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
import pyqtgraph as pg

import numpy as np



class PlotManager:

    """ Abstract class representing a tab that may include 
    a plot """

    def __init__(self, plot_widget, bg='w', styles=None):
        self.plot_widget = plot_widget
        self.plot_widget.setBackground(bg)
        self.legend = None
        self.lines = []
        self.styles = styles
        if styles is None: self.styles = {'color':'black', 'font-size':'17px'}


    def reset_plot (self):
        """ Clear the plot """
        if self.legend:
            self.legend.clear()
        for line in self.lines:
            line.clear()


    def line_plot(self, x, y, *, label=None, width=3, style=Qt.SolidLine, color=None, symbol="o",
                xlabel_pos="bottom", ylabel_pos="left",  xlabel=None, ylabel=None, xgrid=False, ygrid=True):
        """ Method to generate the plot of a single line """
        # Set plot style
        if xlabel: self.plot_widget.setLabel(ylabel_pos, ylabel, **self.styles)
        if ylabel: self.plot_widget.setLabel(xlabel_pos, xlabel, **self.styles)
        self.plot_widget.showGrid(x=xgrid, y=ygrid)
        self.legend = self.plot_widget.addLegend()

        # Define colors
        if color is None:
            color = np.random.randint(0, 255, size=3)
        brush_color = QColor()
        brush_color.setRgb(color[0], color[1], color[2])
        brush = QBrush()
        brush.setColor(brush_color)
        brush.setStyle(Qt.SolidPattern)

        # Plot
        line = self.plot_widget.plot(x, y, name=label,
            pen=pg.mkPen(color=color, width=width, style=style), 
            symbol=symbol,
            symbolSize=4,
            symbolBrush=brush,
        )
        self.lines.append(line)