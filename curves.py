#Fernando Jose Lavarreda Urizar
#Program to analyze Mechanisms, Graduation Project UVG


import re
import csv
from geometry import Curve, Vector, Link, Mechanism, SliderCrank
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
        if self.curves:
            self.select["values"] = (c.name for c in curves)
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
        self.graphics = Graphics(self, (8, 6), row=0, column=0, columnspan=1, rowspan=10, dpi=100, title="")
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
        self.controls.grid(row=10, column=0, rowspan=1, sticky=tk.SE+tk.NW)
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
        self.select = ttk.Combobox(self.controls, state="readonly")
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
            self.select_add_curve["values"] = (c.name for c in self.curves)
    
    
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
           self.temp.curves.append(self.curves[self.select_add_curve.current()].copy())
           self.select_remove_curve["values"] = (*self.select_remove_curve["values"], self.curves[self.select_add_curve.current()].name)
           self.select_add_curve.set('')
           self.load_link(self.temp)
    
    
    def remove_curve(self):
        if self.select_remove_curve.current()!=-1:
            self.temp.curves.pop(self.select_remove_curve.current())
            new_list = list(self.select_remove_curve.current["values"]).pop(self.select_remove_curve.current())
            self.select_remove_curve.current["values"] = tuple(new_list)
            self.select_remove_curve.set('')
    
    
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
        self.select_remove_curve["values"] = (c.name for c in link.curves)
        self.select_remove_curve.set('')
        self.select_connection["values"] = [str(i+1) for i in range(len(link.connections))]
        self.select_connection.set('')
        self.sconnectionx.set('')
        self.sconnectiony.set('')
        if link.curves:
            for c in link.curves:
                self.graphics.static_drawing([[v.x for v in c.vectors], [v.y for v in c.vectors]])



class UIMechanism(ttk.Frame):
    def __init__(self, master, links:List[Link], mechanisms:[Mechanism]):
        super().__init__(master)
        self.links = links
        self.mechanisms = mechanisms
        self.graphics = Graphics(self, (8, 6), row=0, column=0, columnspan=1, rowspan=10, dpi=100, title="")
        self.cursor = -1
        self.temp = None
        #Variables
        self.sname = tk.StringVar(self)
        self.slider = tk.StringVar(self)
        self.soffset = tk.StringVar(self)
        self.srotation = tk.StringVar(self)
        self.crank = None
        self.coupler = None
        self.output = None
        self.ground = None
        #----------
        link_names = [l.name for l in self.links]
        
        self.controls = tk.LabelFrame(self, text="Controls")
        self.controls.grid(row=10, column=0, rowspan=1, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, text="Name:").grid(row=1, column=0, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, text="Connections:").grid(row=0, column=2, sticky=tk.SE+tk.NW, padx=(20, 0))
        ttk.Label(self.controls, text="Rotation (°):").grid(row=0, column=4, sticky=tk.SE+tk.N)
        ttk.Entry(self.controls, textvariable=self.sname).grid(row=1, column=1, sticky=tk.SE+tk.NW)
        ttk.Entry(self.controls, textvariable=self.srotation).grid(row=0, column=5, sticky=tk.SE+tk.NW)
        ttk.Checkbutton(self.controls, text="Slider-Crank", variable=self.slider, onvalue="Offset:", offvalue="Ground:", command=self.change_type).grid(row=0, column=0, sticky=tk.SE+tk.NW)
        
        
        ttk.Label(self.controls, text="Crank:").grid(row=2, column=0, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, text="Coupler:").grid(row=3, column=0, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, text="Output:").grid(row=4, column=0, sticky=tk.SE+tk.NW)
        ttk.Label(self.controls, textvariable=self.slider).grid(row=5, column=0, sticky=tk.SE+tk.NW)
        self.crank = ttk.Combobox(self.controls, values=link_names, state="readonly")
        self.coupler = ttk.Combobox(self.controls, values=link_names, state="readonly")
        self.output = ttk.Combobox(self.controls, values=link_names, state="readonly")
        self.ground = ttk.Combobox(self.controls, values=link_names, state="readonly")
        self.offset_entry = ttk.Entry(self.controls, textvariable=self.sname)
        
        self.connections = [ttk.Combobox(self.controls, state="readonly") for i in range(8)]
        for i, con in enumerate(self.connections):
            con.grid(row=i//2+2, column=i%2+2, sticky=tk.SE+tk.NW, padx=((i+1)%2*20, 0))
        
        
        
        ttk.Button(self.controls, text="new", command=self.new).grid(row=3, column=5, sticky=tk.SE+tk.NW, columnspan=2, padx=(0, 0))
        ttk.Button(self.controls, text="save", command=self.save).grid(row=4, column=5, sticky=tk.SE+tk.NW, columnspan=2, padx=(0, 0))
        ttk.Button(self.controls, text="delete", command=self.delete).grid(row=5, column=5, sticky=tk.SE+tk.NW, columnspan=2, padx=(0, 0))
        self.select = ttk.Combobox(self.controls, state="readonly")
        self.select.bind("<<ComboboxSelected>>", self.selection)
        self.crank.bind("<<ComboboxSelected>>", self.selection)
        self.coupler.bind("<<ComboboxSelected>>", self.selection)
        self.output.bind("<<ComboboxSelected>>", self.selection)
        self.ground.bind("<<ComboboxSelected>>", self.selection)
        self.select.grid(row=2, column=5, sticky=tk.SE+tk.NW, columnspan=2, padx=(0, 0))
        self.crank.grid(row=2, column=1, sticky=tk.SE+tk.NW)
        self.coupler.grid(row=3, column=1, sticky=tk.SE+tk.NW)
        self.output.grid(row=4, column=1, sticky=tk.SE+tk.NW)
        self.ground.grid(row=5, column=1, sticky=tk.SE+tk.NW)
        self.slider.set("Offset:")
        self.slider.set("Ground:")
        #----------------------------
    
    
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
            self.mechanisms.pop(self.cursor)
            counter = 0
            options = []
            for v in self.select["values"]:
                if counter != self.cursor:
                    options.append(v)
                counter+=1
            self.select["values"] = options
            self.select.set('')
            self.load_mechanism(Link(Vector(0, 0), (), (), 0))
            self.cursor = -1
    
    
    def selection(self, comp):
        try:
            available = [self.crank, self.coupler, self.ground]
            i = available.index(comp.widget)
            self.connections[i*2]['values'] = [f'x:{v.x} y:{v.y}' for v in self.links[available[i].current()].connections]
            self.connections[i*2+1]['values'] = [f'x:{v.x} y:{v.y}' for v in self.links[available[i].current()].connections]
        except ValueError:
            #Selection of mechanism
            pass
        
            
    
    
    def change_type(self):
        if self.slider.get()=="Offset:":
            self.ground.grid_forget()
            self.connections[-1]['state'] = 'disabled'
            self.connections[-2]['state'] = 'disabled'
            self.offset_entry.grid(row=5, column=1, sticky=tk.SE+tk.NW)
        else:
            self.offset_entry.grid_forget()
            self.connections[-1]['state'] = 'readonly'
            self.connections[-2]['state'] = 'readonly'
            self.ground.grid(row=5, column=1, sticky=tk.SE+tk.NW)
    
    
    def load_mechanism(self, mechanism:Mechanism|SliderCrank):
        pass
        


    

if __name__ == "__main__":
    wd = tk.Tk()
    #nn = UICurve(wd, [])
    #nn = UILink(wd, [], [])
    nn = UIMechanism(wd, [Link(Vector(0, 0), (), (), 0, name="KK"),], [])
    nn.grid(row=0, column=0)
    wd.mainloop()











