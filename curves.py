#Fernando Jose Lavarreda Urizar
#Program to analyze Mechanisms, Graduation Project UVG


import re
import csv
from geometry import Curve, Vector, Link, Mechanism, SliderCrank, Machine
from typing import Tuple, List
import tkinter as tk
import tkinter.ttk as ttk
from display import Graphics
import tkinter.filedialog as fd
import tkinter.messagebox as msg
from math import sin, cos, tan, pi
import graphics


class UICurve(ttk.Frame):
    def __init__(self, master, curves:List[Curve]):
        super().__init__(master)
        self.curves = curves
        self.graphics = Graphics(self, (9.6, 6), row=0, column=0, columnspan=1, rowspan=10, dpi=100, title="")
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
        self.controls.grid(row=10, column=0, rowspan=1, sticky=tk.SE+tk.NW, pady=(0, 2), padx=(2, 2))
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
        if self.curves:
            self.select["values"] = [c.name for c in curves]
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



class UILink(ttk.Frame):
    def __init__(self, master, curves:List[Curve], links:List[Link]):
        super().__init__(master)
        self.curves = curves
        self.links = links
        self.graphics = Graphics(self, (9.6, 6), row=0, column=0, columnspan=1, rowspan=10, dpi=100, title="")
        self.cursor = -1
        self.temp = None
        #-----------Controls------------
        #Variables
        self.sname = tk.StringVar(self)
        self.sthickness = tk.StringVar(self)
        self.sadd_curve = tk.StringVar(self)
        self.sremove_curve = tk.StringVar(self)
        self.sconnectionx = tk.StringVar(self)
        self.sconnectiony = tk.StringVar(self)
        #--------
        self.controls = tk.LabelFrame(self, text="Controls")
        self.controls.grid(row=10, column=0, rowspan=1, sticky=tk.SE+tk.NW, pady=(0, 2), padx=(2, 2))
        ttk.Label(self.controls, text="Name:").grid(row=0, column=0, sticky=tk.SE+tk.NW)
        ttk.Entry(self.controls, textvariable=self.sname).grid(row=1, column=0, sticky=tk.SE+tk.NW, columnspan=2)
        ttk.Label(self.controls, text="Thickness:").grid(row=2, column=0, sticky=tk.SE+tk.NW)
        ttk.Entry(self.controls, textvariable=self.sthickness).grid(row=3, column=0, sticky=tk.SE+tk.NW, columnspan=2)
        ttk.Label(self.controls, text="Curves:").grid(row=0, column=2, sticky=tk.SE+tk.NW, padx=(25, 0))
        ttk.Button(self.controls, text="add", command=self.add_curve).grid(row=1, column=2, sticky=tk.SE+tk.NW, columnspan=1, padx=(25, 0))
        self.select_add_curve = ttk.Combobox(self.controls, state="readonly")
        ttk.Button(self.controls, text="remove", command=self.remove_curve).grid(row=2, column=2, sticky=tk.SE+tk.NW, columnspan=1, padx=(25, 0))
        self.select_remove_curve = ttk.Combobox(self.controls, state="readonly")
        self.select_add_curve.grid(row=1, column=3, sticky=tk.SE+tk.NW, columnspan=2)
        self.select_remove_curve.grid(row=2, column=3, sticky=tk.SE+tk.NW, columnspan=2)
        ttk.Label(self.controls, text="Connections:").grid(row=0, column=5, sticky=tk.SE+tk.NW, padx=(25, 0))
        ttk.Label(self.controls, text="x:").grid(row=1, column=5, sticky=tk.SE+tk.NW, padx=(25, 0))
        ttk.Entry(self.controls, width=10, textvariable=self.sconnectionx).grid(row=1, column=6, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, text="y:").grid(row=2, column=5, sticky=tk.SE+tk.NW, padx=(25, 0))
        ttk.Entry(self.controls, width=10, textvariable=self.sconnectiony).grid(row=2, column=6, sticky=tk.SE+tk.NW)
        ttk.Button(self.controls, text="add", command=self.add_connection).grid(row=3, column=5, sticky=tk.SE+tk.NW, columnspan=2, padx=(25, 0))
        ttk.Button(self.controls, text="remove", command=self.remove_connection).grid(row=4, column=5, sticky=tk.SE+tk.NW, columnspan=1, padx=(25, 0))
        self.select_connection = ttk.Combobox(self.controls, state="readonly", width=5)
        self.select_connection.grid(row=4, column=6, sticky=tk.SE+tk.NW, columnspan=1)
        ttk.Button(self.controls, text="save", command=self.save).grid(row=2, column=8, sticky=tk.SE+tk.NW, columnspan=2, padx=(25, 0))
        ttk.Button(self.controls, text="new", command=self.new).grid(row=1, column=8, sticky=tk.SE+tk.NW, columnspan=2, padx=(25, 0))
        ttk.Button(self.controls, text="delete", command=self.delete).grid(row=3, column=8, sticky=tk.SE+tk.NW, columnspan=2, padx=(25, 0))
        self.select = ttk.Combobox(self.controls, state="readonly", values=[i.name for i in links])
        self.select.bind("<<ComboboxSelected>>", self.selection)
        self.select_connection.bind("<<ComboboxSelected>>", self.select_conn)
        self.select.grid(row=0, column=8, sticky=tk.SE+tk.NW, columnspan=2, padx=(25, 0))
        self.curves_available()
        #----------------------------
    
    
    def select_conn(self, *args):
        if self.cursor != -1:
            if self.select_connection.current() != -1:
                vec = self.temp.connections[self.select_connection.current()]
                self.sconnectionx.set(str(vec.x))
                self.sconnectiony.set(str(vec.y))
    
    
    def curves_available(self):
        if self.curves:
            self.select_add_curve["values"] = [c.name for c in self.curves]
    
    
    def add_connection(self):
        if self.cursor != -1:
            try:
                x_val = float(self.sconnectionx.get())
                y_val = float(self.sconnectiony.get())
                self.temp.connections.append(Vector(x_val, y_val))
                self.select_connection["values"] = list(self.select_connection["values"])+ [str(len(self.temp.connections))]
            except Exception as e:
                msg.showerror(parent=self, title="Error", message="x,y must be real numbers")
            else:
                self.sconnectionx.set('')
                self.sconnectiony.set('')
    
    
    def remove_connection(self):
        if self.cursor != -1:
            if self.select_connection.current() != -1:
                self.temp.connections.pop(self.select_connection.current())
                self.select_connection["values"] = [str(i+1) for i in range(len(self.temp.connections))]
                self.select_connection.set('')
                self.sconnectionx.set('')
                self.sconnectiony.set('')
    
    
    def add_curve(self):
        if self.select_add_curve.current() != -1:
            if self.temp:
               self.temp.curves.append(self.curves[self.select_add_curve.current()].copy())
               self.select_remove_curve["values"] = (*self.select_remove_curve["values"], self.curves[self.select_add_curve.current()].name)
               self.select_add_curve.set('')
               name = self.sname.get()
               self.load_link(self.temp)
               self.sname.set(name)
            else:
                msg.showerror(parent=self, title="Error", message="No link in workspace, create a new one or load an existing link")
    
    
    def remove_curve(self):
        if self.select_remove_curve.current()!=-1:
            if self.temp:
                self.temp.curves.pop(self.select_remove_curve.current())
                new_list = list(self.select_remove_curve["values"])
                new_list.pop(self.select_remove_curve.current())
                self.select_remove_curve["values"] = tuple(new_list)
                self.select_remove_curve.set('')
                name = self.sname.get()
                self.load_link(self.temp)
                self.sname.set(name)
            else:
                msg.showerror(parent=self, title="Error", message="No link in workspace, create a new one or load an existing link")
    
    
    def save(self):
        if self.cursor != -1:
            try:
                n = float(self.sthickness.get())
                if n<=0:
                    raise ValueError("")
            except Exception:
                msg.showerror(parent=self, title="Error", message="Thickness must be set to a number>0")
            else:
                self.temp.name = self.sname.get()
                self.temp.thickness = float(self.sthickness.get())
                list_options = list(self.select["values"])
                list_options[self.cursor] = self.temp.name
                self.select["values"] = tuple(list_options)
                self.links[self.cursor] = self.temp.copy()
                self.select.set(self.select["values"][self.cursor])
    
    
    def new(self):
        biggest = 1
        for v in self.select["values"]:
            try:
                ff = int(re.search(r"\d+", re.search(r"new\s\d+", v).group()).group())
                if ff>=biggest:
                    biggest = ff+1
            except AttributeError:
                pass
        name = "new "+str(biggest)
        
        nlink = Link(Vector(0, 0), [], [], 0.1, name)
        self.temp = nlink
        self.load_link(self.temp)
        self.links.append(nlink)
        self.cursor = len(self.links)-1
        self.select["values"] = (*self.select["values"], name)
        self.select.set(name)
    
    
    def delete(self):
        if self.cursor != -1:
            self.links.pop(self.cursor)
            counter = 0
            options = []
            for v in self.select["values"]:
                if counter != self.cursor:
                    options.append(v)
                counter+=1
            self.select["values"] = options
            self.select.set('')
            self.load_link(Link(Vector(0, 0), (), (), 0))
            self.cursor = -1
    
    
    def selection(self, *args):
        self.cursor = self.select.current()
        self.temp = self.links[self.cursor].copy()
        self.load_link(self.temp)
    
    
    def load_link(self, link:Link):
        self.graphics.clear()
        self.sname.set(link.name)
        self.sthickness.set(str(round(link.thickness, 6)))
        self.select_remove_curve["values"] = [c.name for c in link.curves]
        self.select_remove_curve.set('')
        self.select_connection["values"] = [str(i+1) for i in range(len(link.connections))]
        self.select_connection.set('')
        self.sconnectionx.set('')
        self.sconnectiony.set('')
        if link.curves:
            for c in link.curves:
                self.graphics.static_drawing([[v.x for v in c.vectors], [v.y for v in c.vectors]])



class UIMechanism(ttk.Frame):
    def __init__(self, master, links:List[Link], mechanisms:List[Mechanism]):
        super().__init__(master)
        self.links = links
        self.mechanisms = mechanisms
        self.graphics = Graphics(self, (9.6, 6), row=0, column=0, columnspan=1, rowspan=10, dpi=100, title="")
        self.cursor = -1
        self.temp = None
        #Variables
        self.sname = tk.StringVar(self)
        self.slider = tk.StringVar(self)
        self.soffset = tk.StringVar(self)
        self.srotation = tk.StringVar(self)
        self.angle_rotate = tk.DoubleVar(self)
        self.inversion = tk.IntVar(self)
        self.crank = None
        self.coupler = None
        self.output = None
        self.ground = None
        #----------
        
        self.controls = tk.LabelFrame(self, text="Controls")
        self.controls.grid(row=10, column=0, rowspan=1, sticky=tk.SE+tk.NW, pady=(0, 2), padx=(2, 2))
        ttk.Label(self.controls, text="Name:").grid(row=1, column=0, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, text="Connections:").grid(row=0, column=2, sticky=tk.SE+tk.NW, padx=(20, 0))
        ttk.Label(self.controls, text="Mech. Rotation (°):").grid(row=0, column=4, sticky=tk.SE+tk.N, padx=(10, 0))
        ttk.Entry(self.controls, textvariable=self.sname).grid(row=1, column=1, sticky=tk.SE+tk.NW)
        ttk.Entry(self.controls, textvariable=self.srotation).grid(row=0, column=5, sticky=tk.SE+tk.NW, padx=(0, 15))
        ttk.Checkbutton(self.controls, text="Slider-Crank", variable=self.slider, onvalue="Offset:", offvalue="Ground:", command=self.change_type).grid(row=0, column=0, sticky=tk.SE+tk.NW)
        
        
        ttk.Label(self.controls, text="Crank:").grid(row=2, column=0, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, text="Coupler:").grid(row=3, column=0, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, text="Output:").grid(row=4, column=0, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, textvariable=self.slider).grid(row=5, column=0, sticky=tk.SE+tk.NW)
        self.crank = ttk.Combobox(self.controls, state="readonly")
        self.coupler = ttk.Combobox(self.controls, state="readonly")
        self.output = ttk.Combobox(self.controls, state="readonly")
        self.ground = ttk.Combobox(self.controls, state="readonly")
        self.offset_entry = ttk.Entry(self.controls, textvariable=self.soffset)
        
        self.connections = [ttk.Combobox(self.controls, state="readonly") for i in range(8)]
        for i, con in enumerate(self.connections):
            con.grid(row=i//2+2, column=i%2+2, sticky=tk.SE+tk.NW, padx=((i+1)%2*20, 0))
        
        
        ttk.Label(self.controls, text="Input angle (°)").grid(row=2, column=4, columnspan=1, sticky=tk.SE+tk.NW, padx=(10, 0))
        ttk.Label(self.controls, textvariable=self.angle_rotate).grid(row=2, column=5, columnspan=1, sticky=tk.SE+tk.NW, padx=(0, 10))
        ttk.Scale(self.controls, variable=self.angle_rotate, from_=0, to=360).grid(row=3, column=4, columnspan=2, sticky=tk.SE+tk.NW, padx=(10, 10))
        
        ttk.Button(self.controls, text="Redraw", command=self.redraw).grid(row=4, column=4, columnspan=2, sticky=tk.SE+tk.NW, padx=(10, 10))
        ttk.Button(self.controls, text="Animate", command=self.animate).grid(row=5, column=4, columnspan=2, sticky=tk.SE+tk.NW, padx=(10, 10))
        
        ttk.Checkbutton(self.controls, text="Inversion", variable=self.inversion, onvalue=1, offvalue=0).grid(row=0, column=6, columnspan=2, sticky=tk.SE+tk.NW, padx=(15, 0))
        ttk.Button(self.controls, text="new", command=self.new).grid(row=3, column=6, sticky=tk.SE+tk.NW, columnspan=2, padx=(15, 0))
        ttk.Button(self.controls, text="save", command=self.save).grid(row=4, column=6, sticky=tk.SE+tk.NW, columnspan=2, padx=(15, 0))
        ttk.Button(self.controls, text="delete", command=self.delete).grid(row=5, column=6, sticky=tk.SE+tk.NW, columnspan=2, padx=(15, 0))
        self.select = ttk.Combobox(self.controls, state="readonly", values=[i.name for i in mechanisms])
        self.select.bind("<<ComboboxSelected>>", self.selection)
        self.crank.bind("<<ComboboxSelected>>", self.selection)
        self.coupler.bind("<<ComboboxSelected>>", self.selection)
        self.output.bind("<<ComboboxSelected>>", self.selection)
        self.ground.bind("<<ComboboxSelected>>", self.selection)
        self.select.grid(row=2, column=6, sticky=tk.SE+tk.NW, columnspan=2, padx=(15, 0))
        self.crank.grid(row=2, column=1, sticky=tk.SE+tk.NW)
        self.coupler.grid(row=3, column=1, sticky=tk.SE+tk.NW)
        self.output.grid(row=4, column=1, sticky=tk.SE+tk.NW)
        self.ground.grid(row=5, column=1, sticky=tk.SE+tk.NW)
        self.slider.set("Offset:")
        self.slider.set("Ground:")
        self.links_available()
        #----------------------------
    
    
    def links_available(self):
        if self.links:
            link_names = [l.name for l in self.links]
            self.crank["values"] = link_names
            self.coupler["values"] = link_names
            self.output["values"] = link_names
            self.ground["values"] = link_names
    
    
    def save(self):
        if self.select.current() != -1:
            try:
                name = self.sname.get()
                specific_msg = "Check rotation"
                rotation = float(self.srotation.get())*pi/180
                crank = self.crank.current()
                coupler = self.coupler.current()
                output = self.output.current()
                crank_connections = [self.connections[0].current(), self.connections[1].current()]
                coupler_connections = [self.connections[2].current(), self.connections[3].current()]
                output_connections = [self.connections[4].current(),]
                if coupler == -1 or crank == -1 or output == -1:
                    specific_msg="Crank, Coupler or Output not selected"
                    raise ValueError("")
                
                if -1 in crank_connections:
                    specific_msg="Missing one or more connections for crank"
                    raise ValueError("")
                if crank_connections[0] == crank_connections[1]:
                    specific_msg="Cannot repeat crank connection"
                    raise ValueError("")
                
                if -1 in coupler_connections:
                    specific_msg="Missing one or more connections for coupler"
                    raise ValueError("")
                if coupler_connections[0] == coupler_connections[1]:
                    specific_msg="Cannot repeat coupler connection"
                    raise ValueError("")
                
                if -1 in output_connections:
                        specific_msg="Missing one or more connections for output"
                        raise ValueError("")
                
                
                
                if self.slider.get() == "Ground:":
                    ground = self.ground.current()
                    ground_connections = [self.connections[6].current(), self.connections[7].current()]
                    output_connections.append(self.connections[5].current())
                    
                    
                    if -1 in output_connections:
                        specific_msg="Missing one or more connections for output"
                        raise ValueError("")
                    
                    if output_connections[0] == output_connections[1]:
                        specific_msg="Missing one or more connections for crank"
                        raise ValueError("")
                    
                    if ground == -1:
                        specific_msg="Ground not selected"
                        raise ValueError("")
                    if -1 in ground_connections:
                        specific_msg="Missing one or more connections for ground"
                        raise ValueError("")
                    
                else:
                    specific_msg="Offset not a number"
                    offset = float(self.soffset.get())
                
            except Exception:
                msg.showerror(parent=self, title="Error", message="Invalid parameters\n"+specific_msg)
            else:
                if self.slider.get() == "Ground:":
                    self.temp = Mechanism(origin=Vector(0, 0), rotation=rotation, links=[self.links[crank].copy(), self.links[coupler].copy(), self.links[output].copy(), self.links[ground].copy()],\
                              connections=[crank_connections, coupler_connections, output_connections, ground_connections], name=name)
                else:
                    self.temp = SliderCrank(origin=Vector(0, 0), rotation=rotation, links=[self.links[crank].copy(), self.links[coupler].copy(), self.links[output].copy()],\
                                connections=[crank_connections, coupler_connections, output_connections], offset=offset, name=name)
                
                list_options = list(self.select["values"])
                list_options[self.select.current()] = self.temp.name
                self.select["values"] = tuple(list_options)
                self.mechanisms[self.select.current()] = self.temp.copy()
                self.select.set(self.select["values"][self.select.current()])
                self.load_mechanism(self.temp)
    
    
    def new(self):
        biggest = 1
        for v in self.select["values"]:
            try:
                ff = int(re.search(r"\d+", re.search(r"new\s\d+", v).group()).group())
                if ff>=biggest:
                    biggest = ff+1
            except AttributeError:
                pass
        name = "new "+str(biggest)
        
        self.temp = None
        self.load_mechanism(self.temp)
        self.mechanisms.append(self.temp)
        self.cursor = len(self.links)-1
        self.select["values"] = (*self.select["values"], name)
        self.select.set(name)
    
    
    def delete(self):
        if self.select.current() != -1:
            self.mechanisms.pop(self.select.current())
            counter = 0
            options = list(self.select["values"])
            options.pop(self.select.current())
            self.select["values"] = options
            self.select.set('')
            self.temp = None
            self.load_mechanism(self.temp)
    
    
    def selection(self, comp):
        if comp.widget == self.select:
            self.load_mechanism(self.mechanisms[self.select.current()])
            self.temp = self.mechanisms[self.select.current()].copy()
            return
        try:
            available = [self.crank, self.coupler, self.output, self.ground]
            i = available.index(comp.widget)
            self.connections[i*2]['values'] = [f'x:{v.x} y:{v.y}' for v in self.links[available[i].current()].connections]
            self.connections[i*2+1]['values'] = [f'x:{v.x} y:{v.y}' for v in self.links[available[i].current()].connections]
        except ValueError:
            #Selection of mechanism, shouldn't happen
            pass
    
    
    def change_type(self):
        if self.slider.get()=="Offset:":
            self.ground.grid_forget()
            self.connections[-1]['state'] = 'disabled'
            self.connections[-2]['state'] = 'disabled'
            self.connections[5]['state'] = 'disabled'
            self.offset_entry.grid(row=5, column=1, sticky=tk.SE+tk.NW)
        else:
            self.offset_entry.grid_forget()
            self.connections[-1]['state'] = 'readonly'
            self.connections[-2]['state'] = 'readonly'
            self.connections[5]['state'] = 'readonly'
            self.ground.grid(row=5, column=1, sticky=tk.SE+tk.NW)
    
    
    def load_mechanism(self, mechanism:Mechanism|SliderCrank, animate_:bool=False):
        self.graphics.clear()
        if mechanism == None:
            return
        
        self.sname.set(mechanism.name)
        self.srotation.set(str(round(mechanism.rotation*180/pi, 2)))
        self.crank.set(mechanism.links[0].name)
        self.coupler.set(mechanism.links[1].name)
        self.output.set(mechanism.links[2].name)
        
        self.connections[0]['values'] = [f'x:{v.x} y:{v.y}' for v in mechanism.links[0].connections]
        self.connections[1]['values'] = [f'x:{v.x} y:{v.y}' for v in mechanism.links[0].connections]
        self.connections[2]['values'] = [f'x:{v.x} y:{v.y}' for v in mechanism.links[1].connections]
        self.connections[3]['values'] = [f'x:{v.x} y:{v.y}' for v in mechanism.links[1].connections]
        self.connections[4]['values'] = [f'x:{v.x} y:{v.y}' for v in mechanism.links[2].connections]
        self.connections[5]['values'] = [f'x:{v.x} y:{v.y}' for v in mechanism.links[2].connections]
        
        
        self.connections[0].current(mechanism.connections[0][0])
        self.connections[1].current(mechanism.connections[0][1])
        
        self.connections[2].current(mechanism.connections[1][0])
        self.connections[3].current(mechanism.connections[1][1])
        
        self.connections[4].current(mechanism.connections[2][0])
        
        
        if self.crank.current() == -1:
            msg.showwarning("Warning", message="Crank link has been deleted or its name has changed if new changes are going to be saved to the mechanism check for the correct link")
        if self.coupler.current() == -1:
            msg.showwarning("Warning", message="Coupler link has been deleted or its name has changed if new changes are going to be saved to the mechanism check for the correct link")
        if self.output.current() == -1:
            msg.showwarning("Warning", message="Output link has been deleted or its name has changed if new changes are going to be saved to the mechanism check for the correct link")
        
        
        if type(mechanism) == Mechanism:
            self.slider.set("Ground:")
            self.ground.set(mechanism.links[3].name)
            
            self.connections[6]['values'] = [f'x:{v.x} y:{v.y}' for v in mechanism.links[3].connections]
            self.connections[7]['values'] = [f'x:{v.x} y:{v.y}' for v in mechanism.links[3].connections]
            self.connections[5].current(mechanism.connections[2][1])
            self.connections[6].current(mechanism.connections[3][0])
            self.connections[7].current(mechanism.connections[3][1])
            
            if self.ground.current() == -1:
                msg.showwarning("Warning", message="Ground link has been deleted or its name has changed if new changes are going to be saved to the mechanism check for the correct link")
            
        
        elif type(mechanism) == SliderCrank:
            self.sname.set(mechanism.name)
            self.slider.set("Offset:")
            self.soffset.set(mechanism.c)
            
            if self.crank.current() == -1:
                msg.showwarning("Warning", message="Crank link has been deleted or its name has changed if new changes are going to be saved to the mechanism check for the correct link")
            if self.coupler.current() == -1:
                msg.showwarning("Warning", message="Coupler link has been deleted or its name has changed if new changes are going to be saved to the mechanism check for the correct link")
            if self.output.current() == -1:
                msg.showwarning("Warning", message="Output link has been deleted or its name has changed if new changes are going to be saved to the mechanism check for the correct link")
        
        self.change_type()
        
        if animate_:
            animation = graphics.plot_rotation_mech(mechanism, frames=100, inversion=self.inversion.get(), axes=self.graphics.axis, fig=self.graphics.fig)
        else:
            solution = mechanism.solution(self.angle_rotate.get()*pi/180)[self.inversion.get()]
            graphics.plot_mechanism(*solution, self.graphics.axis)
        
        self.graphics.render()
    
    
    def redraw(self, *args):
        if self.temp:
            self.load_mechanism(self.temp)
            return
        msg.showerror("Error", message="Mechanism must be saved before")
    
    
    def animate(self, *arga):
        if self.temp:
            self.load_mechanism(self.temp, animate_=True)
            return
        msg.showerror("Error", message="Mechanism must be saved before")



class UIMachine(ttk.Frame):
    def __init__(self, master, mechanisms:List[Mechanism], machines:List[Machine]):
        super().__init__(master)
        self.mechanisms = mechanisms
        self.machines = machines
        self.graphics = Graphics(self, (9.6, 6), row=0, column=0, columnspan=1, rowspan=10, dpi=100, title="")
        self.temp = None
        self.temp_mechanisms = []
        #Variables
        self.sname = tk.StringVar(self)
        self.angle_rotate = tk.DoubleVar(self)
        self.bsave_image = tk.BooleanVar(self)
        self.spower_graph = tk.StringVar(self)
        self.sinversion_array = tk.StringVar(self)
        #----------
        self.controls = tk.LabelFrame(self, text="Controls")
        self.controls.grid(row=10, column=0, rowspan=1, sticky=tk.SE+tk.NW, pady=(0, 2), padx=(2, 2))
        
        ttk.Label(self.controls, text="Name:").grid(row=0, column=0, columnspan=1, sticky=tk.SE+tk.NW, pady=(10, 0))
        ttk.Entry(self.controls, textvariable=self.sname).grid(row=0, column=1, columnspan=1, sticky=tk.SE+tk.NW, pady=(10, 0))
        
        ttk.Label(self.controls, text="Mechanisms:").grid(row=1, column=0, columnspan=1, sticky=tk.SE+tk.NW)
        self.integrating_mech = ttk.Combobox(self.controls, state="readonly")
        self.integrating_mech.grid(row=1, column=1, columnspan=1, sticky=tk.SE+tk.NW)
        ttk.Button(self.controls, text="remove", command=self.remove_mech).grid(row=2, column=0, columnspan=2, sticky=tk.SE+tk.NW)
        
        ttk.Label(self.controls, text="Mechanism Library:").grid(row=3, column=0, columnspan=1, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, text="Available:").grid(row=4, column=0, columnspan=1, sticky=tk.SE+tk.NW)
        self.available_mechanisms = ttk.Combobox(self.controls, state="readonly")
        self.available_mechanisms.grid(row=4, column=1, columnspan=1, sticky=tk.SE+tk.NW)
        ttk.Button(self.controls, text="add", command=self.add_mech).grid(row=5, column=0, columnspan=2, sticky=tk.SE+tk.NW)
        
        ttk.Label(self.controls, text="Power Graph:").grid(row=0, column=2, columnspan=1, sticky=tk.SE+tk.NW, padx=(3, 0))
        ttk.Entry(self.controls, textvariable=self.spower_graph).grid(row=1, column=2, columnspan=2, sticky=tk.SE+tk.NW, padx=(10, 0))
        ttk.Label(self.controls, text="Inversion Array:").grid(row=2, column=2, columnspan=1, sticky=tk.SE+tk.NW, padx=(3, 0))
        ttk.Entry(self.controls, textvariable=self.sinversion_array).grid(row=3, column=2, columnspan=2, sticky=tk.SE+tk.NW, padx=(10, 0))
        
        ttk.Checkbutton(self.controls, text="Save Image/Video", variable=self.bsave_image, onvalue=True, offvalue=False).grid(row=1, column=5, sticky=tk.SE+tk.NW, padx=(5, 0))
        ttk.Label(self.controls, text="Input angle (°)").grid(row=2, column=4, columnspan=1, sticky=tk.SE+tk.NW, padx=(10, 0))
        ttk.Label(self.controls, textvariable=self.angle_rotate).grid(row=2, column=5, columnspan=1, sticky=tk.SE+tk.NW, padx=(0, 10))
        ttk.Scale(self.controls, variable=self.angle_rotate, from_=0, to=360).grid(row=3, column=4, columnspan=2, sticky=tk.SE+tk.NW, padx=(10, 10))
        
        ttk.Button(self.controls, text="Redraw", command=self.redraw).grid(row=4, column=4, columnspan=2, sticky=tk.SE+tk.NW, padx=(10, 10))
        ttk.Button(self.controls, text="Animate", command=self.animate).grid(row=5, column=4, columnspan=2, sticky=tk.SE+tk.NW, padx=(10, 10))
        
        ttk.Button(self.controls, text="new", command=self.new).grid(row=3, column=6, sticky=tk.SE+tk.NW, columnspan=2, padx=(15, 0))
        ttk.Button(self.controls, text="save", command=self.save).grid(row=4, column=6, sticky=tk.SE+tk.NW, columnspan=2, padx=(15, 0))
        ttk.Button(self.controls, text="delete", command=self.delete).grid(row=5, column=6, sticky=tk.SE+tk.NW, columnspan=2, padx=(15, 0))
        self.select = ttk.Combobox(self.controls, state="readonly", values=[i.name for i in machines])
        self.select.bind("<<ComboboxSelected>>", self.selection)
        self.select.grid(row=2, column=6, sticky=tk.SE+tk.NW, columnspan=2, padx=(15, 0))
        self.mechanisms_available()
    
    
    def mechanisms_available(self):
        if self.mechanisms:
            self.available_mechanisms["values"] = [v.name for v in self.mechanisms]
    
    
    def check_power_graph(self):
        inp = self.spower_graph.get().strip()
        graph = []
        stack = []
        current = ""
        incomplet_graph = {}
        max_ = None
        numbers = [f"{i}" for i in range(10)]
        symbols_ = ""
        if len(inp) == 0:
            raise ValueError(f"Invalid power graph")
        
        for i, m in enumerate(inp):
            if m in numbers:
                current+=m
                symbols_+=m
            elif m == "{" or m == "}":
                if current == "":
                    if m == "}" and symbols_[-1] == "{":
                        stack = []
                        symbols_+=m
                        continue
                    else:
                        raise ValueError(f"Invalid input at position {i+1}")
                stack.append(int(current))
                if max_ == None or int(current)>max_:
                    max_ = int(current)
                current = ""
                symbols_+=m
                if m == "}":
                    incomplet_graph[stack[0]] = stack[1:]
                    stack = []
            elif m == " ":
                continue
            elif m == ",":
                if current == "" or len(stack) == 0:
                    raise ValueError(f"Invalid input at position {i+1}")
                stack.append(int(current))
                if int(current)>max_:
                    max_ = int(current)
                current = ""
            else:
                raise ValueError("Invalid input "+ m + f" at position {i+1}")
        
        graph = [[] for i in range(max_+1)]
        for i in range(max_+1):
            if i in incomplet_graph:
                graph[i] = incomplet_graph[i]
            else:
                graph[i] = []
        return graph
    
    
    def check_inversion_array(self):
        inp = self.sinversion_array.get()
        if inp == "0" or inp == "1":
            return int(inp)
        m = re.fullmatch("[01]+", inp)
        if m:
            return [int(i) for i in m.group()]
        raise ValueError("Inversion array not valid must be a series of 0s and 1s or a single 0 or 1")
    
    
    def save(self):
        if self.select.current() != -1:
            try:
                pw_graph = self.check_power_graph()
                name = self.sname.get()
                self.temp = Machine(self.temp_mechanisms, pw_graph, name)
            except ValueError as e:
                msg.showerror(parent=self, title="Error", message=str(e))
            except AssertionError as e:
                msg.showerror(parent=self, title="Error", message=str(e))
            else:
                
                list_options = list(self.select["values"])
                list_options[self.select.current()] = self.temp.name
                self.select["values"] = list_options
                self.machines[self.select.current()] = self.temp.copy()
                self.select.set(self.select["values"][self.select.current()])
                self.load_machine(self.temp)
    
    
    def new(self):
        biggest = 1
        for v in self.select["values"]:
            try:
                ff = int(re.search(r"\d+", re.search(r"new\s\d+", v).group()).group())
                if ff>=biggest:
                    biggest = ff+1
            except AttributeError:
                pass
        name = "new "+str(biggest)
        
        self.temp = None
        self.machines.append(self.temp)
        self.select["values"] = (*self.select["values"], name)
        self.select.set(name)
        self.load_machine(self.temp)
        self.temp_mechanisms = []
    
    
    def delete(self):
        if self.select.current() != -1:
            self.machines.pop(self.select.current())
            counter = 0
            options = list(self.select[values])
            options.pop(self.select.current())
            self.select["values"] = options
            self.select.set('')
            self.temp = None
            self.load_machine(self.temp)
            self.temp_mechanisms = []
    
    
    def remove_mech(self):
        if self.integrating_mech.current() != -1:
            if self.temp != None:
                self.temp.mechanisms.pop(self.integrating_mech.current())
            v = list(self.integrating_mech['values'])
            v.pop(self.integrating_mech.current())
            self.integrating_mech["values"] = v
            self.temp_mechanisms.pop(self.integrating_mech.current())
            self.integrating_mech.set('')
    
    
    def add_mech(self):
        if self.available_mechanisms.current() != -1:
            if self.mechanisms[self.available_mechanisms.current()] == None:
                msg.showerror(parent=self, title="Error", message="Cannot add a mechanism that has not been saved")
                return
            self.temp_mechanisms.append(self.mechanisms[self.available_mechanisms.current()].copy())
            self.integrating_mech["values"] = [*self.integrating_mech["values"], self.mechanisms[self.available_mechanisms.current()].name]
    
    
    def selection(self, *args):
        self.load_machine(self.machines[self.select.current()])
        self.temp = self.machines[self.select.current()].copy()
    
    
    def load_machine(self, machine:Machine, animate_:bool=False):
        self.graphics.clear()
        if machine != None:
            self.sname.set(machine.name)
            if self.sinversion_array.get().strip() == "":
                self.sinversion_array.set(1)
            self.temp_mechanisms = [mech.copy() for mech in machine.mechanisms]
            self.integrating_mech["values"] = [mech.name for mech in machine.mechanisms]
            self.spower_graph.set(''.join([str(i)+"{"+','.join([str(o) for o in machine.power_graph[i]])+"}" for i in range(len(machine.power_graph))]))
            try:
                inversions = self.check_inversion_array()
            except ValueError as e:
                msg.showerror(parent=self, title="Error", message=str(e))
            else:
                if animate_:
                    self.load_machine(machine)
                    xlims = [abs(x) for x in list(self.graphics.axis.get_xlim())]
                    ylims = [abs(y) for y in list(self.graphics.axis.get_ylim())]
                    biggest = max(ylims+xlims)
                    xlims[0] = biggest*-1.15
                    xlims[1] = biggest*1.15
                    ylims[0] = biggest*-1.15
                    ylims[1] = biggest*1.15
                    self.graphics.clear()
                    self.graphics.render()
                    animation = graphics.plot_rotation_mach(machine, frames=100, lims=[xlims, ylims], inversion=inversions, axes=self.graphics.axis, fig=self.graphics.fig)
                else:
                    solution = machine.solution(self.angle_rotate.get()*pi/180, inversions)
                    graphics.plot_machine(solution, self.graphics.axis)
                
                self.graphics.render()
    
    
    def redraw(self, *args):
        if self.temp:
            self.load_machine(self.temp)
            return
        msg.showerror("Error", message="Machine must be saved before")
    
    
    def animate(self, *args):
        if self.temp:
            self.load_machine(self.temp, animate_=True)
            return
        msg.showerror("Error", message="Machine must be saved before")



class GUI(tk.Tk):
    def __init__(self, curves:List[Curve]=[], links:List[Link]=[], mechanisms:List[Mechanism|SliderCrank]=[], machines:List[Machine]=[]):
        super().__init__()
        self.notebook = ttk.Notebook(self)
        self.curves = curves
        self.links = links
        self.mechanisms = mechanisms
        self.machines = machines
        self.geometry(f"+{self.winfo_screenwidth()//6}+0")
        self.resizable(False, False)
        self.title("KASM")
        
        self.pages = {
            "Curves": UICurve(self.notebook, self.curves),
            "Links":  UILink(self.notebook, self.curves, self.links),
            "Mechanisms": UIMechanism(self.notebook, self.links, self.mechanisms),
            "Machines": UIMachine(self.notebook, self.mechanisms, self.machines)
        }
        
        for key, value in self.pages.items():
            self.notebook.add(value, text=key, underline=0, sticky=tk.NE + tk.SW)
        
        self.notebook.bind("<<NotebookTabChanged>>", self.change_page)
        self.notebook.enable_traversal()
        self.notebook.pack()
    
    
    def change_page(self, *args):
        self.pages["Links"].curves_available()
        self.pages["Mechanisms"].links_available()
        self.pages["Machines"].mechanisms_available()



if __name__ == "__main__":
    import examples
    #wd = tk.Tk()
    mac = examples.build_compresor(12)
    
    c1 = Curve(Vector(0, 0), [Vector(x/20, (x/20)**2) for x in range(11)])
    c2 = Curve(Vector(0, 0), [Vector(x/20, (x/20-1)**2) for x in range(10, 21)])
    c3 = Curve(Vector(0, 0), [Vector(0, 0), Vector(1, 0)])
    hc1 = Curve(Vector(0, 0), [Vector(x/40, 1+(0.25-(x/40-0.5)**2)**0.5) for x in range(41)])
    hc2 = Curve(Vector(0, 0), [Vector(x/40, -1-(0.25-(x/40-0.5)**2)**0.5) for x in range(41)])
    jcurve = Curve(Vector(0, 0), [Vector(0, 1), Vector(0, -1)])
    jcurve2 = Curve(Vector(0, 0), [Vector(1, 1), Vector(1, -1)])
    bc1 = Curve(Vector(0, 0), [Vector(x/20, -(x/20)**2) for x in range(21)])
    bc2 = Curve(Vector(0, 0), [Vector(x/20, -(x/20-2)**2) for x in range(20, 41)])
    bc3 = Curve(Vector(0, 0), [Vector(0, 0), Vector(2, 0)])
    
    
    link = Link(Vector(0, 0), [Vector(0, 0), Vector(1, 0)], [c1, c2, c3], 0.0, name="crank")
    link2 = Link(Vector(0, 0), [Vector(0.5, 1.25), Vector(0.5, -1.25)], [hc1.copy(), hc2.copy(), jcurve.copy(), jcurve2.copy()], 0.0, name="coupler")
    link3 = Link(Vector(0, 0), [Vector(0.5, 1.25), Vector(0.5, -1.25)], [hc1, hc2, jcurve, jcurve2], 0.0, name="output")
    link4 = Link(Vector(0, 0), [Vector(0, 0), Vector(2, 0)], [bc1, bc2, bc3], 0.0, name="ground")
    mech = Mechanism(Vector(0, 0), -0.2*pi, [link, link2, link3, link4], ((0, 1), (0, 1), (0, 1), (0, 1)), name="Paco")
    
    #nn = UICurve(wd, [])
    #nn = UILink(wd, [], [])
    #nn = UIMechanism(wd, [link, link2, link3, link4], [mech,])
    #nn = UIMachine(wd, [mech,], [mac,])
    #nn.grid(row=0, column=0)
    #wd.mainloop()
    #gui = GUI(mechanisms=[mech,], machines=[mac,])
    gui = GUI()
    gui.mainloop()
    




