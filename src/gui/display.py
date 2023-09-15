#Fernando Jose Lavarreda Urizar
#Program to analyze Mechanisms, Graduation Project UVG, Free & Open Source


import tkinter as tk
from typing import Tuple, List
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
from matplotlib.figure import Figure


class Graphics():
    
    def __init__(self, parent, size:Tuple[int, int], row, column, columnspan, rowspan, dpi:int, title="", remove_ticks=True):
        self.fig = Figure(figsize=size, dpi=dpi)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=column, row=row, rowspan=rowspan, columnspan=columnspan, sticky=tk.SE+tk.NW)
        self.axis = self.fig.add_subplot(111)
        self.axis.set_title(title)
        self.fig.tight_layout()
        if remove_ticks:
            self.axis.set_xticklabels([])
            self.axis.set_xticks([])
            self.axis.set_yticks([])
            self.axis.set_yticklabels([])
    
    
    def render(self):
        self.canvas.draw()
        self.canvas.flush_events()
    
    
    def clear(self):
        self.axis.cla()
        self.render()
    
    
    def set_lims(self, xlims:Tuple[float, float], ylims:Tuple[float, float]):
        self.axis.axis(xmin=xlims[0], xmax=xlims[1], ymin=ylims[0], ymax=ylims[1])
        self.render()
    
    
    def make_animation(self, sequence:Tuple[List[List[float]], List[List[float]]], *, time_out:float=0):
        line = self.axis.plot(sequence[0][0], sequence[1][0])[0]
        if len(str(self.axis.get_yticks()[0]))>4:
            self.axis.set_yticklabels(self.axis.get_yticks(), rotation=70)
        self.render()
        for frame in range(len(sequence[0])):
            line.set_data(sequence[0][frame], sequence[1][frame])
            time.sleep(time_out)
            self.render()
    
    
    def static_drawing(self, sequence:Tuple[List[float], List[float]], grid=False):
        self.axis.plot(sequence[0], sequence[1])
        #if len(str(self.axis.get_yticks()[0]))>4:
        #    self.axis.set_yticklabels(self.axis.get_yticks(), rotation=70)
        if not grid:
            self.axis.set_xticklabels([])
            self.axis.set_xticks([])
            self.axis.set_yticks([])
            self.axis.set_yticklabels([])
        else:
            self.axis.grid(visible=grid)
        self.render()
    
    
    def moving(self):
        self.set_lims([-1.2*4/3, 1.2*4/3], [-1.2, 1.2])
        xs = [[0, math.cos(i/1_000*2*math.pi)] for i in range(1_000)]
        ys = [[0, math.sin(i/1_000*2*math.pi)] for i in range(1_000)]
        self.make_animation([xs, ys], time_out=0)