#Fernando Jose Lavarreda Urizar
#Program to analyze Mechanisms, Graduation Project UVG


import re
import csv
from geometry import Curve, Vector
from typing import Tuple, List
import tkinter as tk
import tkinter.ttk as ttk
from display import Graphics
import tkinter.filedialog as fd
import tkinter.messagebox as msg
from math import sin, cos, tan



class UICurve(ttk.Frame):
    def __init__(self, master, curves:List[Curve]):
        super().__init__(master)
        self.curves = curves
        self.graphics = Graphics(self, (8, 6), row=0, column=0, columnspan=1, rowspan=10, dpi=100, title="")
        self.cursor = -1
        self.temp = None
        #------------Control of Curve Properties------------------
        #Variables
        self.smovex = tk.StringVar(self)
        self.smovey = tk.StringVar(self)
        self.srotate = tk.StringVar(self)
        self.sname = tk.StringVar(self)
        self.sfunctions = tk.StringVar(self)
        #-----
        self.controls = tk.LabelFrame(self, text="Controls")
        self.controls.grid(row=10, column=0, rowspan=1, sticky=tk.SE+tk.NW)
        self.name = ttk.Entry(self.controls, textvariable=self.sname)
        self.functions = ttk.Entry(self.controls, textvariable=self.sfunctions)
        self.movex = ttk.Entry(self.controls, width=10, textvariable=self.smovex)
        self.movey = ttk.Entry(self.controls, width=10, textvariable=self.smovey)
        self.rotate_angle = ttk.Entry(self.controls, width=5, textvariable=self.srotate)
        ttk.Label(self.controls, text="Name:").grid(row=0, column=0, sticky=tk.SE+tk.NW)
        self.name.grid(row=1, column=0, sticky=tk.SE+tk.NW, columnspan=2)
        ttk.Label(self.controls, text="Functions:").grid(row=2, column=0, sticky=tk.SE+tk.NW)
        self.functions.grid(row=3, column=0, sticky=tk.SE+tk.NW, columnspan=2)
        ttk.Label(self.controls, text="Data:").grid(row=2, column=2, sticky=tk.SE+tk.NW, columnspan=1, padx=(15,0))
        ttk.Button(self.controls, text="upload", command=self.upload).grid(row=3, column=2, sticky=tk.SE+tk.N, columnspan=1, padx=(15,0))
        ttk.Button(self.controls, text="clear", command=self.clear).grid(row=3, column=3, sticky=tk.SE+tk.N, columnspan=1)
        ttk.Label(self.controls, text="Translate:").grid(row=0, column=4, sticky=tk.SE+tk.NW, columnspan=2, padx=(15,0))
        ttk.Label(self.controls, text="x:").grid(row=1, column=4, sticky=tk.SE+tk.NW, columnspan=1, padx=(15, 0))
        ttk.Label(self.controls, text="y:").grid(row=2, column=4, sticky=tk.SE+tk.NW, columnspan=1, padx=(15, 0))
        self.movex.grid(row=1, column=5, sticky=tk.SE+tk.NW, columnspan=1)
        self.movey.grid(row=2, column=5, sticky=tk.SE+tk.NW, columnspan=1)
        ttk.Button(self.controls, text="move", command=self.move).grid(row=3, column=4, sticky=tk.SE+tk.NW, columnspan=2, padx=(15, 0))
        ttk.Label(self.controls, text="Rotate:").grid(row=0, column=6, sticky=tk.SE+tk.NW, columnspan=2, padx=(15,0))
        ttk.Label(self.controls, text="Angle(°)").grid(row=1, column=6, sticky=tk.SE+tk.NW, columnspan=1, padx=(15,0))
        self.rotate_angle.grid(row=1, column=7, sticky=tk.SE+tk.NW, columnspan=1)
        ttk.Button(self.controls, text="rotate", command=self.rotate).grid(row=3, column=6, sticky=tk.SE+tk.NW, columnspan=2, padx=(15, 0))
        ttk.Button(self.controls, text="save", command=self.save).grid(row=2, column=8, sticky=tk.SE+tk.NW, columnspan=2, padx=(25, 0))
        ttk.Button(self.controls, text="new", command=self.new).grid(row=1, column=8, sticky=tk.SE+tk.NW, columnspan=2, padx=(25, 0))
        ttk.Button(self.controls, text="delete", command=self.delete).grid(row=3, column=8, sticky=tk.SE+tk.NW, columnspan=2, padx=(25, 0))
        self.select = ttk.Combobox(self.controls, state="readonly")
        self.select.bind("<<ComboboxSelected>>", self.selection)
        self.select.grid(row=0, column=8, sticky=tk.SE+tk.NW, columnspan=2, padx=(25, 0))
        self.functions.bind("<Return>", self.func)
        #------------------------------
    
    
    def func(self, *args):
        m = re.match("[\d|\.|(sin)|(cos)|(tan)|x|\*|\+|\-|/|\(|\)]*\{(-?\d+\.?\d*,\s*){2}(\d+\s*){1}\}", self.sfunctions.get())
        vectors = []
        if m != None:
            evaluate = m.group()
            limits = re.findall("-?\d+\.?\d*", evaluate)[-3:]
            evaluate = evaluate[:evaluate.find('{')]
            start = float(limits[0])
            end = float(limits[1])
            samples = int(limits[2])
            if start>=end:
                msg.showerror(parent=self, title="Error", message="End can't be smaller than beginning \n(limits of the function)")
                return
            try:
                dx = (end-start)/samples
                for i in range(samples):
                    result = eval(evaluate.replace("x", "("+str(start)+")"))
                    vectors.append(Vector(start, result))
                    start+=dx
            except Exception as e:
                msg.showerror(parent=self, title="Error", message="Couldn't evaluate expression")
            else:
                self.temp.vectors = [*self.temp.vectors]+vectors
                self.temp.functions = self.sfunctions.get()
                self.load_curve(self.temp)
        else:
            msg.showerror(parent=self, title="Error", message="Couldn't interpret expression")
    
    
    def upload(self, *args):
        if self.cursor != -1:
            rd = fd.askopenfilename(parent=self, title="Load Data", filetypes=(("CSV", "*.csv"),("CSV", "*.txt")))
            if rd:
                add = []
                with open(rd, newline="") as file:
                    reader = csv.reader(file, delimiter=",")
                    for line in reader:
                        add.append(Vector(*line))
                self.temp.vectors = [*self.temp.vectors]+add
                self.load_curve(self.temp)
    
    
    def clear(self):
        if self.temp != None:
            self.temp.vectors = ()
            self.load_curve(self.temp)
    
    
    def move(self):
        try:
            vx = float(self.smovex.get())
            vy = float(self.smovey.get())
        except Exception:
            msg.showerror(parent=self, title="Error", message="Translations must have real values")
        else:
            self.temp.translate(vx, vy)
            self.load_curve(self.temp)
    
    
    def rotate(self):
        try:
            v = float(self.srotate.get())
        except Exception:
            msg.showerror(parent=self, title="Error", message="Rotation must have real values")
        else:
            self.temp.rotate_angle(v)
            self.load_curve(self.temp)
    
    
    def delete(self):
        if self.cursor != -1:
            self.curves.pop(self.cursor)
            counter = 0
            options = []
            for v in self.select["values"]:
                if counter != self.cursor:
                    options.append(v)
                counter+=1
            self.select["values"] = options
            self.select.set('')
            self.load_curve(Curve(Vector(0, 0), ()))
            self.cursor = -1
    
    
    def save(self, *args):
        if self.cursor != -1:
            self.temp.name = self.sname.get()
            self.temp.functions = self.sfunctions.get()
            list_options = list(self.select["values"])
            list_options[self.cursor] = self.temp.name
            self.select["values"] = tuple(list_options)
            self.curves[self.cursor] = self.temp.copy()
            self.select.set(self.select["values"][self.cursor])
    
    
    def new(self, *args):
        biggest = 1
        for v in self.select["values"]:
            try:
                ff = int(re.search(r"\d+", re.search(r"new\s\d+", v).group()).group())
                if ff>=biggest:
                    biggest = ff+1
            except AttributeError:
                pass
        name = "new "+str(biggest)
        
        ncurve = Curve(Vector(0, 0), (), name)
        self.temp = ncurve
        self.load_curve(self.temp)
        self.curves.append(ncurve)
        self.cursor = len(self.curves)-1
        self.select["values"] = (*self.select["values"], name)
        self.select.set(name)
        #self.graphics.set_lims([0, 1], [0, 1])
    
    
    def selection(self, *args):
        self.cursor = self.select.current()
        self.temp = self.curves[self.cursor].copy()
        self.load_curve(self.temp)
    
    
    def load_curve(self, curve:Curve):
        self.graphics.clear()
        self.sname.set(curve.name)
        self.sfunctions.set(curve.functions)
        self.smovex.set("0")
        self.smovey.set("0")
        self.srotate.set("0")
        if len(curve.vectors):
            self.graphics.static_drawing([[v.x for v in curve.vectors], [v.y for v in curve.vectors]])
        
    

if __name__ == "__main__":
    wd = tk.Tk()
    nn = UICurve(wd, [])
    nn.grid(row=0, column=0)
    wd.mainloop()











