#Fernando Jose Lavarreda Urizar
#Program to analyze Mechanisms, Graduation Project UVG

import csv
import numpy as np
import numpy.linalg as linalg
from typing import List, Tuple, Mapping, Callable
from math import sin, cos, pi, sqrt, atan, atan2, asin


def angle_rad(angle:float):
    return angle*pi/180


def rad_angle(rad:float):
    return rad*180/pi


class Vector:
    def __init__(self, x, y):
        """Representation of 2D-Vector"""
        self.x = x
        self.y = y

    
    def rotate(self, angle:float):
        self.x, self.y = self.x*cos(angle)-self.y*sin(angle), self.x*sin(angle)+self.y*cos(angle)
    
    
    def rotate_angle(self, angle:float):
        self.rotate(angle_rad(angle))
    
    
    def translate(self, x, y):
        self.y+=y
        self.x+=x
    
    
    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y)
    
    
    def __sub__(self, other):
        return Vector(self.x-other.x, self.y-other.y)
    
    
    def __str__(self):
        return f"Vector: \nx: {self.x}\ny: {self.y}\n"
    
    
    def size(self):
        return sqrt(self.x*self.x+self.y*self.y)
    
    
    def copy(self):
        return Vector(self.x, self.y)



def vector_length(a:Vector, b:Vector):
    """Return the distance between two vectors"""
    return sqrt((b.x-a.x)**2+(b.y-a.y)**2)


def vector_angle(a:Vector, b:Vector):
    """Get the angle between two position"""
    return atan2(b.y-a.y, b.x-a.x)


def build_callable_function(string:str):
    """Build function from string"""
    def function(x:float):
        call = string.replace("x", str(x))
        return eval(call)
    return function


class Function:
    def __init__(self, start:float, end:float, process:Callable[[float], float]=None, string_function=""):
        assert start<end, f"Start must be smaller than end, {start}, {end}"
        assert (process != None) ^ (string_function != ""), "Either process xor string_function must be valid"
        self.start = start
        self.end = end
        if process:
            self.func = process
        else:
            self.func = build_callable_function(string_function)
    
    
    def __call__(self, value:float):
        if value < self.start or value > self.end:
            raise ValueError(f"{value} out of bounds, limits: [{self.start}, {self.end}]")
        return self.func(value)
    
    
    def centroid(self, dx:float=1e-10):
        nvalue = self.start+dx
        area = 0
        xcoord_numerator = 0
        ycoord_numerator = 0
        while nvalue < self.end:
            compute = abs(self(nvalue)*dx)
            xcoord_numerator+= compute*nvalue
            ycoord_numerator+= compute*self(nvalue)/2
            area+=compute
        centroid_ = Vector(xcoord_numerator/area, ycoord_numerator/area)
        return centroid_, area
    
    
    def __sub__(self, other):
        """Create new Function from substracting one from another"""
        assert type(other) == type(self), "Can only substract self from other Function"
        if self.start < other.start:
            start = other.start
        else:
            start = self.start
        if self.end > other.end:
            end = other.end
        else:
            end = self.end
        
        def call_(x:float):
            return self(x)-other(x)
        
        return Function(start, end, call_)
    
    
    def __add__(self, other):
        """Create new Function from adding one from another"""
        assert type(other) == type(self), "Can only substract self from other Function"
        if self.start < other.start:
            start = other.start
        else:
            start = self.start
        if self.end > other.end:
            end = other.end
        else:
            end = self.end
        
        def call_(x:float):
            return self(x)+other(x)
        
        return Function(start, end, call_)
    
    
    def concatenate(self, other):
        """Create new Function from putting one next to the other, smallest start 
           Function has precedence. Undefined behaviour is out of bounds 
           for both functions (space in between) and therefore replaced with linear interpolation
           between the last and first value of each one of the funcitons"""
        if self.start <= other.start:
            if self.end <  other.end:
                if self.end < other.start:
                    m = other(other.start)/self(self.end)
                    def function(x:float):
                        if x <= self.end:
                            return self.func(x)
                        elif x < other.start:
                            return m*(x-self.end)+self(self.end)
                        else:
                            return other.func(x)
                else:
                    def function(x:float):
                        if x <= self.end:
                            return self.func(x)
                        else:
                            return other.func(x)
                return Function(self.start, other.end, function)
            return Function(self.start, self.end, self.func)
        
        other.concatenate(self)


    
def concatenate_functions(functions:List[Function]):
    ordered = sorted(functions, key=lambda x: x.start)
    fn = ordered[0]
    for f in ordered[1:]:
        fn = fn.concatenate(f)
    return fn
    


class Curve:
    def __init__(self, origin:Vector, vectors:List[Vector], name="", functions="", function:Function=None):
        """Series of Vectors to create a profile
           origin: Absolute position where the start of the Curve is located"""
        self.vectors = vectors
        self.origin = origin
        self.name = name
        self.functions = functions
        self.function = function
        if self.function:
            self.computable_centroid = True
        else:
            self.computable_centroid = False
    
    
    @staticmethod
    def build_from_io(file_descriptor, delimiter=",", origin=Vector(0, 0), multiple=False):
        reader = csv.reader(file_descriptor, delimiter=delimiter)
        header = next(reader)
        vectors = []
        for line in reader:
            if "New" in line[0]:
                if multiple:
                    vectors.append([])
            elif "Point" in line[0]:
                next(reader)
            else:
                try:
                    x = float(line[0])
                    y = float(line[1])
                except ValueError:
                    raise ValueError("Un able to process token: ", line[0])
                else:
                    if multiple:
                        vectors[-1].append(Vector(x, y))
                    else:
                        vectors.append(Vector(x, y))
        if multiple:
            curves = []
            for v in vectors:
                curves.append(Curve(origin, v))
            return curves
        return Curve(origin, vectors)
    
    
    def rotate(self, angle:float):
        for v in self.vectors:
            v.rotate(angle)
        self.computable_centroid = False
    
    
    def rotate_angle(self, angle:float):
        self.rotate(angle_rad(angle))
    
    
    def translate(self, x:float, y:float)->Vector:
        for v in self.vectors:
            v.translate(x, y)
        self.computable_centroid = False
    
    
    def absolute(self):
        return Curve(self.origin, [v+self.origin for v in self.vectors])
    
    
    def copy(self):
        curve = Curve(self.origin.copy(), [v.copy() for v in self.vectors], self.name, self.functions, self.function)
        curve.computable_centroid = self.computable_centroid
        return curve



class Link:
    def __init__(self, origin:Vector, connections:List[Vector], curves:List[Curve], thickness:float, name="", upper:List[Function]=[], lower:List[Function]=[], centroid=None):
        """A link is a segment of a mechanism for which the position and stress are desired
           origin: Absolute position where the start of the Link is located
           connections: Vectors where another link may be connected to create a mechanism
           curves: groups of curve that define the link's shape
           thickness: depth of the link, important only if stresses are to be calculated
           name: helps as identifier of the link
           upper: list of Function that define the upper bound of the link,
                  only important to define when calculating stresses
           lower: list of Function that define the lower bound of the link,
                  only important to define when calculating stresses"""
        
        self.origin = origin
        self.connections = connections
        self.curves = curves
        self.thickness = thickness
        self.name = name
        self.translation = Vector(0, 0)
        self.rotation = 0
        self.upper = upper
        self.lower = lower
        self.centroid_vector = centroid
        self.mass = 0
        self.moment_inertia_centroid  = 0
        self.element_node_locations = [] #List[Vector] indicating the centroid for each element for Finite Element Analysis
        self.areas = []
        self.inertias = []
        self.heights = [] #Heights for each node being analyzed, required for stresses due to momentum (Mc/I )
    
    
    @staticmethod
    def build_from_io(file_descriptor, delimiter=",", origin=Vector(0, 0)):
        reader = csv.reader(file_descriptor, delimiter=delimiter)
        header = next(reader)
        vectors = []
        connections = []
        for line in reader:
            if "New" in line[0]:
                vectors.append([])
            elif "Point" in line[0]:
                advance = next(reader)
                connections.append(Vector(float(advance[0]), float(advance[1])))
            else:
                try:
                    x = float(line[0])
                    y = float(line[1])
                except ValueError:
                    raise ValueError("Un able to process token: ", line[0])
                else:
                    vectors[-1].append(Vector(x, y))
        
        curves = []
        for v in vectors:
            curves.append(Curve(origin, v))
        
        return Link(origin, connections, curves, 0.1)
    
    
    def rotate(self, angle:float):
        for curve in self.curves:
            curve.rotate(angle)
        
        for conn in self.connections:
            conn.rotate(angle)
        
        if self.centroid_vector:
            self.centroid_vector.rotate(angle)
            for v in self.element_node_locations:
                v.rotate(angle)
        
        self.rotation+=angle
    
    
    def rotate_angle(self, angle:float):
        self.rotate(angle_rad(angle))
    
    
    def translate(self, x:float, y:float):
        for curve in self.curves:
            curve.translate(x, y)
        
        for conn in self.connections:
            conn.translate(x, y)
        
        if self.centroid_vector:
            self.centroid_vector.translate(x, y)
            for v in self.element_node_locations:
                v.translate(x, y)
        
        self.translation+=Vector(x, y)
    
    
    def absolute(self):
        return Link(self.origin, [conn+self.origin for conn in self.connections], [c.absolute() for c in self.curves], thickness, name, upper=self.upper[:], lower=self.lower[:])
    
    
    def length(self, a, b):
        """Get the length between two connection points in the Link, 0 based"""
        assert a < len(self.connections), "a argument is out of bounds"
        assert b < len(self.connections), "b argument is out of bounds"
        return vector_length(self.connections[a], self.connections[b])
    
    
    def set_lims(self, indexes:List[int], lims=1):
        """Set functions defining limits of the link to calculate stresses"""
        functions_ = []
        for v in indexes:
            if v >= len(self.curves) or v < 0:
                raise ValueError(f"{v} is out of bounds, Curves is only size {len(self.curves)}")
            if self.curves[v].function == None or not self.curves[v].computable_centroid:
                raise ValueError(f"Curve {self.curves[v]} with index {v} has no function defining it or has been rotated, therefore is not valid")
            functions_.append(self.curves[v].function)
        
        if lims:
            self.upper = functions_
        else:
            self.lower = functions_
    
    
    def centroid(self, dx:float, density:float, tolerance:float=1e-3):
        """To speed up calculation intesection between curves is not evaluated,
           make sure upper curve is above lower curve throughout the domain
           centroid must be computed before translating and/or rotating the Link
           proceed with the calculation of mass and moment of intertia around centroid"""
        if not self.upper or not self.lower:
            raise ValueError("Either lower or upper limits are missing")
        
        up_function = concatenate_functions(self.upper)
        lo_function = concatenate_functions(self.lower)
        if abs(up_function.start-lo_function.start)>tolerance or abs(up_function.end-lo_function.end)>tolerance:
            raise ValueError("End and start of functions defining the upper and lower bounds is greater than tolerance accepeted")
        self.element_node_locations = []
        self.areas = []
        self.inertias = []
        self.heights = []
        area = 0
        position = dx/2+up_function.start
        ycoord_numerator = 0
        xcoord_numerator = 0 #Repeating similar process to Function computation of centroid because the y coordinate will not be accurate when substracting the upper and lower bounds of the link
        while position < up_function.end:
            evaluate_high = up_function(position)
            evaluate_low = lo_function(position)
            compute = dx*(evaluate_high-evaluate_low)
            area+=compute
            y_centroid = (evaluate_high-evaluate_low)/2+evaluate_low
            xcoord_numerator+=position*compute
            ycoord_numerator+=y_centroid*compute
            self.heights.append((evaluate_high-evaluate_low)/2)
            self.element_node_locations.append(Vector(position, y_centroid))
            self.areas.append(self.thickness*(evaluate_high-evaluate_low))
            self.inertias.append(self.thickness/12*(evaluate_high-evaluate_low)*(evaluate_high-evaluate_low)*(evaluate_high-evaluate_low)) #Second moment of area
            position+=dx
        
            
        
        self.centroid_vector = Vector(xcoord_numerator/area, ycoord_numerator/area)
        self.area = area
        position = dx/2+up_function.start
        dy = dx
        darea = dx*dy
        xo = self.centroid_vector.x
        yo = self.centroid_vector.y
        polar_moment_area = 0
        while position < up_function.end:
            evaluate_high = up_function(position)
            evaluate_low = lo_function(position)
            compute = (evaluate_high-evaluate_low)
            positiony = evaluate_low+dy/2
            
            precom_pute = (position-xo)*(position-xo)
            while positiony < evaluate_high:
                polar_moment_area+=darea*(precom_pute+(positiony-yo)*(positiony-yo))
                positiony+=dy
            
            position+=dx
        self.mass = self.thickness*area*density
        self.moment_inertia_centroid = self.thickness*polar_moment_area*density
        return self.centroid_vector
    
    
    def copy(self):
        link = Link(self.origin.copy(), [conn.copy() for conn in self.connections], [c.copy() for c in self.curves], self.thickness, self.name, upper=self.upper[:], lower=self.lower[:])
        if self.centroid_vector:
            link.centroid_vector = self.centroid_vector.copy()
            link.mass = self.mass
            link.moment_inertia_centroid = self.moment_inertia_centroid
            link.element_node_locations = [i.copy() for i in self.element_node_locations]
            link.areas = self.areas[:]
            link.inertias = self.inertias[:]
            link.heights = self.heights[:]
        return link



class Mechanism:
    def __init__(self, origin:Vector, rotation:float, links:List[Link], connections:List[Tuple[int, int]], init=True, name="", stress_analysis:bool=False, dx:float=0, density:float=0):
        """Representation of 4 bar mechanism, must be ordered as follows: a (crank), b (coupler), c (output), d (bench/ground)
           connections: numbers indicating the connection points from the links to use"""
        assert len(connections) == len(links), "Missmatch between connections and links"
        assert len(links) == 4, "Can only solve for 4 bar mechanism"
        self.name = name
        self.origin = origin
        self.links = [l.copy() for l in links]
        self.connections = connections
        self.moved = Vector(0,0)
        self.idisplacement = Vector(0, 0)
        self.a = links[0].length(connections[0][0], connections[0][1])
        self.b = links[1].length(connections[1][0], connections[1][1])
        self.c = links[2].length(connections[2][0], connections[2][1])
        self.d = links[3].length(connections[3][0], connections[3][1])
        self.k1 = self.d/self.a
        self.k2 = self.d/self.c
        self.k3 = (self.a*self.a-self.b*self.b+self.c*self.c+self.d*self.d)/(2*self.a*self.c)
        self.k4 = self.d/self.b
        self.k5 = (self.c*self.c-self.d*self.d-self.a*self.a-self.b*self.b)/(2*self.a*self.b)
        self.size = (self.a+self.b)*1.1
        self.stress_analysis = stress_analysis
        
        if stress_analysis:
            assert dx>0, "Requiring a dx>0 for stress analysis"
            assert density>0, "Requiring a density>0 for stress analysis"
            for link in self.links:
                link.centroid(dx, density)
        
        if rotation > 2*pi:
            self.rotation = angle_rad(rotation)
        else:
            self.rotation = rotation
        
        
        if init:
            self.initial_placement()
        
    
    def location(self):
        return self.origin+self.moved
        
    
    
    def initial_placement(self):
        """This method allows to change the rotation and position of a mechanism that has already been created
           Useful when copying a mechanism and desiring to change rotation and location of the new one"""
        self.links[3].rotate(self.rotation)
        self.idisplacement = self.origin-self.links[3].connections[self.connections[3][0]]
        self.links[3].translate(self.idisplacement.x, self.idisplacement.y)
        
        for i in range(3):
            
            if i == 2:
                self.links[i].translate(-self.links[i].connections[self.connections[i][1]].x, -self.links[i].connections[self.connections[i][1]].y)
                self.links[i].rotate(vector_angle(self.links[i].connections[self.connections[i][1]], self.links[i].connections[self.connections[i][0]])+self.rotation+pi)
                #Do not know why but this fixed the error
                if abs(vector_angle(self.links[i].connections[self.connections[i][1]], self.links[i].connections[self.connections[i][0]])+self.rotation+pi-pi*2)<1e-10:
                    self.links[i].rotate(pi)
            else:
                self.links[i].translate(-self.links[i].connections[self.connections[i][0]].x, -self.links[i].connections[self.connections[i][0]].y)
                self.links[i].rotate(-vector_angle(self.links[i].connections[self.connections[i][0]], self.links[i].connections[self.connections[i][1]])+self.rotation)
    
    
    def copy(self):
        mechanism = Mechanism(self.origin.copy(), self.rotation, links=self.links[:], connections=[i for i in self.connections], init=False, name=self.name)
        mechanism.stress_analysis = self.stress_analysis
        mechanism.translate(self.moved.x, self.moved.y)
        return mechanism
    
    
    def translate(self, x:float, y:float):
        self.moved += Vector(x, y)
    
    
    def rotate(self, angle:float):
        movement_ground = self.idisplacement + self.moved
        self.links[3].translate(-movement_ground.x, -movement_ground.y)
        self.links[3].rotate(angle)
        for i in range(3):
            self.links[i].rotate(angle)
        self.links[3].translate(movement_ground.x, movement_ground.y)
        self.rotation+=angle
    
    
    def rotate_angle(self, angle:float):
        self.rotate(angle_rad(angle))
    
    
    def output_rad(self, input_rad:float):
        """input_rad: crank angle relative to ground in rads
        raise a ValueError if the crank can't be placed in that position"""
        A = cos(input_rad)-self.k1-self.k2*cos(input_rad)+self.k3
        B = -2*sin(input_rad)
        C = self.k1-(self.k2+1)*cos(input_rad)+self.k3
        
        try:
            solution_a = 2*atan((-B+sqrt(B*B-4*A*C))/2/A)
            solution_b = 2*atan((-B-sqrt(B*B-4*A*C))/2/A)
        except ValueError:
            if (B*B-4*A*C) < -1e-15:
                raise ValueError("Crank can't be put in that position")
            else:
                solution_a = 2*atan((-B)/2/A)
                solution_b = solution_a
        except ZeroDivisionError:
            if (-B+sqrt(B*B-4*A*C)) < 0:
                solution_a = -pi
            else:
                solution_a = pi
            if (-B-sqrt(B*B-4*A*C)) < 0:
                solution_b = -pi
            else:
                solution_b = pi
        return solution_a, solution_b
    
    
    def output_angle(self, input_angle:float):
        """input_angle: crank angle relative to ground in degrees
        raise a ValueError if the crank can't be placed in that position"""
        a, b = self.output_rad(angle_rad(input_angle))
        return rad_angle(a), rad_angle(b)
    
    
    def coupler_rad(self, input_rad:float):
        """input_rad: crank angle relative to ground in rads
        raise a ValueError if the crank can't be placed in that position"""
        D = cos(input_rad)-self.k1+self.k4*cos(input_rad)+self.k5
        E = -2*sin(input_rad)
        F = self.k1+(self.k4-1)*cos(input_rad)+self.k5
        
        try:
            solution_a = 2*atan((-E+sqrt(E*E-4*D*F))/2/D)
            solution_b = 2*atan((-E-sqrt(E*E-4*D*F))/2/D)
        except ValueError:
            raise ValueError("Crank can't be put in that position")
        
        return solution_a, solution_b
    
    
    def coupler_angle(self, input_angle:float):
        """input_angle: crank angle relative to ground in degrees
        raise a ValueError if the crank can't be placed in that position"""
        a, b = coupler_rad(angle_rad(input_angle))
        return rad_angle(a), rad_angle(b)
    
    
    def angular_velocity(self, input_rad1:float, input_rad2:float, dt:float, inversion:int):
        """input_rad1: crank angle relative to ground in rads
           input_rad2: second crank angle relative to ground in rads
           dt: time between the two positions
           Ground has an angular speeds of 0
        raise a ValueError if the crank can't be placed in that position"""
        assert inversion == 1 or inversion == 0, "Inversion can only by 0 or 1"
        w_crank = (input_rad2-input_rad1)/dt
        w_coupler = (self.coupler_rad(input_rad2)[inversion]-self.coupler_rad(input_rad1)[inversion])/dt 
        w_output = (self.output_rad(input_rad2)[inversion]-self.output_rad(input_rad1)[inversion])/dt
        return w_crank, w_coupler, w_output, 0
    
    
    def angular_velocity_angular_acceleration(self, input_rad:float, crank_angular_speed_rad:float, crank_angular_acceleration_rad:float, inversion:int):
        """Obtain tuples with angular speed and acceleration of each link"""
        coupler_rad = self.coupler_rad(input_rad)[inversion]
        output_rad = self.output_rad(input_rad)[inversion]
        coupler_speed  = crank_angular_speed_rad*self.a/self.b*sin(output_rad-input_rad)/sin(coupler_rad-output_rad)
        output_speed = crank_angular_speed_rad*self.a/self.c*sin(input_rad-coupler_rad)/sin(output_rad-coupler_rad)
        
        A = self.c*sin(output_rad)
        B = self.b*sin(coupler_rad)
        C = self.a*crank_angular_acceleration_rad*sin(input_rad)+self.a*crank_angular_speed_rad**2*cos(input_rad)+self.b*coupler_speed**2*cos(coupler_rad)-self.c*output_speed**2*cos(output_rad)
        D = self.c*cos(output_rad)
        E = self.b*cos(coupler_rad)
        F = self.a*crank_angular_acceleration_rad*cos(input_rad)-self.a*crank_angular_speed_rad**2*sin(input_rad)-self.b*coupler_speed**2*sin(coupler_rad)+self.c*output_speed**2*sin(output_rad)
        
        coupler_acceleration = (C*D-A*F)/(A*E-B*D)
        output_acceleration = (C*E-B*F)/(A*E-B*D)
        ground_speed = 0
        ground_acceleration = 0
        return [(crank_angular_speed_rad, crank_angular_acceleration_rad), (coupler_speed, coupler_acceleration), (output_speed, output_acceleration), (ground_speed, ground_acceleration)]
    
    
    def solution(self, angle_rad:float):
        """Absolute position given an input angle for crank in radians
           Return value might be: one solution repeated twice, two different solutions
           or ValueError if this position is not possible"""
        ca, cb = self.coupler_rad(angle_rad)
        oa, ob = self.output_rad(angle_rad)
        
        crank = self.links[0].copy()
        coupler = self.links[1].copy()
        coupler2 = self.links[1].copy()
        output = self.links[2].copy()
        output2 = self.links[2].copy()
        ground = self.links[3].copy()
        
        
        crank.rotate(angle_rad)
        coupler.rotate(ca)
        coupler2.rotate(cb)
        output.rotate(oa)
        output2.rotate(ob)
        
        crank.translate(self.origin.x, self.origin.y)
        crank.translate(self.moved.x, self.moved.y)
        ground.translate(self.moved.x, self.moved.y)
        coupler.translate(crank.connections[self.connections[0][1]].x, crank.connections[self.connections[0][1]].y)
        coupler2.translate(crank.connections[self.connections[0][1]].x, crank.connections[self.connections[0][1]].y)
        output.translate(ground.connections[self.connections[3][1]].x, ground.connections[self.connections[3][1]].y)
        output2.translate(ground.connections[self.connections[3][1]].x, ground.connections[self.connections[3][1]].y)
        
        
        return [crank, coupler, output, ground], [crank, coupler2, output2, ground]



class SliderCrank:
    def __init__(self, origin:Vector, rotation:float, links:List[Link], connections:List[Tuple[int, int]], offset:float=0, init=True, name="", stress_analysis:bool=False, dx:float=0, density:float=0):
        """Representation of 4 bar mechanism, must be ordered as follows: a (crank), b (coupler), c (output), d (bench/ground)
           Ground is an optional addition to the links
           connections: numbers indicating the connection points from the links to use"""
        assert len(connections) == len(links), "Missmatch between connections and links"
        assert len(links) == 3 or len(links) == 4, "Can only solve for 4 bar mechanism, ground link is optional"
        
        self.name = name
        self.origin = origin
        self.links = [l.copy() for l in links]
        self.connections = connections
        self.moved = Vector(0,0)
        self.idisplacement = Vector(0, 0)
        self.a = links[0].length(connections[0][0], connections[0][1])
        self.b = links[1].length(connections[1][0], connections[1][1])
        self.c = offset
        self.size = (self.a+self.b)*1.1
        self.stress_analysis = stress_analysis
        
        if stress_analysis:
            assert dx>0, "Requiring a dx>0 for stress analysis"
            assert density>0, "Requiring a density>0 for stress analysis"
            for link in self.links:
                link.centroid()
        
        #Ground optional
        if len(links) == 3:
            gg = Curve(Vector(0, 0), [Vector(0,0,),])
            self.links.append(Link(Vector(0, 0), [Vector(0, 0)], [gg,], 0.0))
            self.connections.append([0,])
        
        if rotation > 2*pi:
            self.rotation = angle_rad(rotation)
        else:
            self.rotation = rotation
        
        
        if init:
            self.initial_placement()
        
    
    def location(self):
        return self.origin+self.moved
    
    
    def initial_placement(self):
        """This method allows to change the rotation and position of a mechanism that has already been created
           Useful when copying a mechanism and desiring to change rotation and location of the new one"""
        self.links[3].rotate(self.rotation)
        self.idisplacement = self.origin-self.links[3].connections[self.connections[3][0]]
        self.links[3].translate(self.idisplacement.x, self.idisplacement.y)
        
        for i in range(3):
            
            if i == 2:
                self.links[i].translate(-self.links[i].connections[self.connections[i][0]].x, -self.links[i].connections[self.connections[i][0]].y)
                self.links[i].rotate(self.rotation)
            elif i == 1:
                self.links[i].translate(-self.links[i].connections[self.connections[i][1]].x, -self.links[i].connections[self.connections[i][1]].y)
                self.links[i].rotate(-vector_angle(self.links[i].connections[self.connections[i][0]], self.links[i].connections[self.connections[i][1]])+self.rotation+pi)
            else:
                self.links[i].translate(-self.links[i].connections[self.connections[i][0]].x, -self.links[i].connections[self.connections[i][0]].y)
                self.links[i].rotate(-vector_angle(self.links[i].connections[self.connections[i][0]], self.links[i].connections[self.connections[i][1]])+self.rotation)
    
    
    def copy(self):
        slider_crank = SliderCrank(self.origin.copy(), self.rotation, links=self.links, connections=[i for i in self.connections], offset=self.c, init=False, name=self.name)
        slider_crank.stress_analysis = self.stress_analysis
        slider_crank.translate(self.moved.x, self.moved.y)
        return slider_crank
    
    
    def translate(self, x:float, y:float):
        self.moved += Vector(x, y)
    
    
    def rotate(self, angle:float):
        movement_ground = self.idisplacement + self.moved
        self.links[3].translate(-movement_ground.x, -movement_ground.y)
        self.links[3].rotate(angle)
        for i in range(3):
            self.links[i].rotate(angle)
        self.links[3].translate(movement_ground.x, movement_ground.y)
        self.rotation+=angle
    
    
    def rotate_angle(self, angle:float):
        self.rotate(angle_rad(angle))
    
    
    def output_rad(self, input_rad:float, coupler_rotation:float):
        """input_rad: crank angle relative to ground in rads
           coupler_rotation: rotation of the coupler in rads
           Returns a distance"""
        d = self.a*cos(input_rad)-self.b*cos(coupler_rotation)
        return d
    
    
    def output_angle(self, input_angle:float, coupler_rotation:float):
        """input_rad: crank angle relative to ground in degrees
            coupler_rotation: rotation of the coupler in degrees
            Returns a distance"""
        d = self.output_rad(angle_rad(input_angle), angle_rad(coupler_rotation))
        return d
    
    
    def coupler_rad(self, input_rad:float):
        """input_rad: crank angle relative to ground in rads
        raise a ValueError if the crank can't be placed in that position"""
        try:
            solution_a = asin((self.a*sin(input_rad)-self.c)/self.b)
            solution_b = asin(-(self.a*sin(input_rad)-self.c)/self.b)+pi
        except ValueError:
            raise ValueError("Crank can't be put in that position")
        
        return solution_a, solution_b
    
    
    def coupler_angle(self, input_angle:float):
        """input_angle: crank angle relative to ground in degrees
        raise a ValueError if the crank can't be placed in that position"""
        a, b = self.coupler_rad(angle_rad(input_angle))
        return rad_angle(a), rad_angle(b)
    
    
    def angular_velocity(self, input_rad1:float, input_rad2:float, dt:float, inversion:int):
        """input_rad1: crank angle relative to ground in rads
           input_rad2: second crank angle relative to ground in rads
           dt: time between the two positions. 
           Ground and output have angular speeds of 0
        raise a ValueError if the crank can't be placed in that position"""
        assert inversion == 1 or inversion == 0, "Inversion can only by 0 or 1"
        w_crank = (input_rad2-input_rad1)/dt
        w_coupler = (self.coupler_rad(input_rad2)[inversion]-self.coupler_rad(input_rad1)[inversion])/dt 
        return w_crank, w_coupler, 0, 0
    
    
    def angular_velocity_angular_acceleration(self, input_rad:float, crank_angular_speed_rad:float, crank_angular_acceleration_rad:float, inversion:int):
        """Obtain tuples with angular speed and acceleration of each link
           For output it is linear velocity and acceleration since the slider has no rotation"""
        coupler_rad = self.coupler_rad(input_rad)[inversion]
        coupler_speed  = crank_angular_speed_rad*self.a/self.b*cos(input_rad)/cos(coupler_rad)
        output_speed = -self.a*crank_angular_speed_rad*sin(input_rad)+self.b*coupler_speed*sin(coupler_rad)
        
        coupler_acceleration = (self.a*crank_angular_acceleration_rad*cos(input_rad)-self.a*crank_angular_speed_rad**2*sin(input_rad)+self.b*coupler_speed**2*sin(coupler_rad))/(self.b*cos(coupler_rad))
        output_acceleration = -self.a*crank_angular_acceleration_rad*sin(input_rad)-self.a*crank_angular_speed_rad**2*cos(input_rad)+self.b*coupler_acceleration*sin(coupler_rad)+self.b*coupler_speed**2*cos(coupler_rad)
        ground_speed = 0
        ground_acceleration = 0
        return [(crank_angular_speed_rad, crank_angular_acceleration_rad), (coupler_speed, coupler_acceleration), (output_speed, output_acceleration), (ground_speed, ground_acceleration)]
    
    
    def solution(self, angle_rad:float):
        """Absolute position given an input angle for crank in radians
           Return value might be: one solution repeated twice, two different solutions
           or ValueError if this position is not possible"""
        ca, cb = self.coupler_rad(angle_rad)
        oa = self.output_rad(angle_rad, ca)
        ob = self.output_rad(angle_rad, cb)
        
        crank = self.links[0].copy()
        coupler = self.links[1].copy()
        coupler2 = self.links[1].copy()
        output = self.links[2].copy()
        output2 = self.links[2].copy()
        ground = self.links[3].copy()
        
        
        crank.rotate(angle_rad)
        coupler.rotate(ca)
        coupler2.rotate(cb)
        
        crank.translate(self.origin.x, self.origin.y)
        crank.translate(self.moved.x, self.moved.y)
        ground.translate(self.moved.x, self.moved.y)
        mv_coupler = crank.connections[self.connections[0][1]]-coupler.connections[self.connections[1][0]]
        mv_coupler2 = crank.connections[self.connections[0][1]]-coupler2.connections[self.connections[1][0]]
        coupler.translate(mv_coupler.x, mv_coupler.y)
        coupler2.translate(mv_coupler2.x, mv_coupler2.y)
        mv_out = coupler.connections[self.connections[1][1]]-output.connections[self.connections[2][0]]
        mv_out2 = coupler2.connections[self.connections[1][1]]-output2.connections[self.connections[2][0]]
        output.translate(mv_out.x, mv_out.y)
        output2.translate(mv_out2.x, mv_out2.y)
        
        
        return [crank, coupler, output, ground], [crank, coupler2, output2, ground]



class Machine:
    def __init__(self, mechanisms:List[Mechanism], power_graph:List[List[int]], auto_adjust:bool=False, name:str=""):
        """A machine is defined here as one or more 4-bar mechanisms connected
           - First Mechanism must be the input mechanism
           - power_graph: indicates what a mechanism powers. It is a list of lists where list 0 represents the input crank from the first mechanism
             so mechanism '0' is represented in list as '1'. Example: [[1, 3], [], [], [2]] in this example the input crank powers mechanism 1 and 3 and mechanism 3 powers mechanism 2
             if a mechanism doesn't power anything place an empty list. Bear in mind mechanism 2 will only be powered by the output of mechanism 3.
           - auto_adjust: indicates if mechanisms should be translated to the corresponding output
           - Important to consider that a mechanism cannot be powered by more than one output, if this happens only the last one will be taken as power
           - SliderCrank cannot power any mechanism
        """
        assert all([type(mechanisms[i]) != SliderCrank or len(power_graph[i+1]) == 0 for i in range(len(mechanisms))]), "Slider cannot power another mechanism"
        assert 1 in power_graph[0], "Mechanism 1 must be powered by its own crank"
        
        self.name = name
        self.mechanisms = mechanisms[:]
        self.power_graph = power_graph
        self.input_graph = [-1 for i in range(len(power_graph))]
        for power in range(len(power_graph)):
            for receiver in power_graph[power]:
                self.input_graph[receiver] = power
        
        if -1 in self.input_graph[1:]:
            raise ValueError("One or more mechanisms are not powered")
        
        if auto_adjust:
            for m in range(1, len(self.input_graph)):
                powered_mech_connection = self.mechanisms[m-1].connections[-1][0] #Ground connection of slave mechanism Index
                if self.input_graph[m]:
                    powering_mech = self.input_graph[m]-1
                    powering_mech_connection_to_attach = self.mechanisms[powering_mech].connections[-1][1] #Ground connection of commander mechanism Index
                    displacement = self.mechanisms[powering_mech].links[-1].connections[powering_mech_connection_to_attach]-self.mechanisms[m-1].links[-1].connections[powered_mech_connection]
                    displacement+= self.mechanisms[powering_mech].moved
                else:
                    powering_mech_connection_to_attach = self.mechanisms[0].connections[0][0] #Ground connection of commander mechanism Index
                    displacement = self.mechanisms[0].links[0].connections[powering_mech_connection_to_attach]-self.mechanisms[m-1].links[0].connections[powered_mech_connection]
                self.mechanisms[m-1].translate(displacement.x, displacement.y)
    
    
    def copy(self):
        return Machine(mechanisms=[m.copy() for m in self.mechanisms], power_graph=self.power_graph, name=self.name)
    
    
    def angular_velocity(self, input_rad1:float, input_rad2:float, dt:float, pattern:list=0):
        """input_rad1: main crank angle relative to ground in rads
           input_rad2: second main crank angle relative to ground in rads
           dt: time between the two positions. 
           pattern: indicates the inversions for each mechanism
           angular velocities are returned for each one of the mechanisms in the order of creation of the Machine
        raise a ValueError if the crank can't be placed in that position"""
        sorting = topological_sort(self.power_graph)[1:]
        snapshot_1 = self.solution(input_rad1, pattern)
        snapshot_2 = self.solution(input_rad2, pattern)
        velocities = [0 for i in range(len(self.mechanisms))]
        for i in range(len(snapshot_1)):
            velocities_single_mechanism = [(snapshot_2[i][x].rotation-snapshot_1[i][x].rotation)/dt for x in range(len(snapshot_1[i])) ]
            velocities[sorting[i]-1] = velocities_single_mechanism
        return velocities
    
    
    def solution(self, angle_rad:float, pattern:list=0)->List[List[Link]]:
        inversions = None
        solutions = [0 for i in range(len(self.mechanisms)+1)]
        if type(pattern) == list:
            if len(pattern) != len(self.mechanisms):
                raise ValueError("Incorrect inversion, must be a single 1 or 0 or a list of 1s and 0s for each mechanism")
            inversions = pattern
        elif pattern:
            inversions = [1 for i in range(len(self.mechanisms))]
        else:
            inversions = [0 for i in range(len(self.mechanisms))]
        
        snapshot = []
        
        sorting = topological_sort(self.power_graph)
        solutions[0] = self.mechanisms[0].rotation+angle_rad
        counter = 1
        for mechanism_ in sorting[1:]:
            n_solution = self.mechanisms[mechanism_-1].solution(solutions[self.input_graph[mechanism_]]-self.mechanisms[mechanism_-1].rotation)[inversions[mechanism_-1]]
            snapshot.append(n_solution)
            if self.power_graph[mechanism_]:
                solutions[mechanism_] = self.mechanisms[mechanism_-1].output_rad(solutions[self.input_graph[mechanism_]]-self.mechanisms[mechanism_-1].rotation)[inversions[mechanism_-1]]+self.mechanisms[mechanism_-1].rotation
        
        return snapshot
    
    
    def solution_kinetics(self, angle_rad:float, speed_rad:float, acceleration_rad:float, external_moments_cranks:List[float]=[], external_moments_couplers:List[float]=[], pattern:list=0):
        assert all([m.stress_analysis for m in self.mechanisms]), "All mechanisms must have a centroid and mass to find the forces"
        assert len(external_moments_cranks) == len(self.mechanisms) or len(external_moments_cranks) == 1 or len(external_moments_cranks) == 0, "Must provide an external moment for each mechanism or just for the last one"
        assert len(external_moments_couplers) == len(self.mechanisms) or len(external_moments_couplers) == 1 or len(external_moments_couplers) == 0, "Must provide an external moment for each mechanism or just for the last one"
        assert all([type(m) == Mechanism for m in self.mechanisms]), "Stresses have only been implemented to four link-pin mechanisms. No SliderCrank, nor any other type"
        
        if len(external_moments_couplers) == 0 and len(external_moments_cranks) == 0:
            raise ValueError("No external torque is being applied")
        
        inversions = None
        solutions = [0 for i in range(len(self.mechanisms)+1)]
        accelerations = [[] for i in range(len(self.mechanisms)+1)]
        if type(pattern) == list:
            if len(pattern) != len(self.mechanisms):
                raise ValueError("Incorrect inversion, must be a single 1 or 0 or a list of 1s and 0s for each mechanism")
            inversions = pattern
        elif pattern:
            inversions = [1 for i in range(len(self.mechanisms))]
        else:
            inversions = [0 for i in range(len(self.mechanisms))]
        
        snapshot = []
        sorting = topological_sort(self.power_graph)
        solutions[0] = self.mechanisms[0].rotation+angle_rad
        accelerations[0] = ((speed_rad, acceleration_rad), (speed_rad, acceleration_rad), (speed_rad, acceleration_rad), (speed_rad, acceleration_rad))
        linear_and_angular_accelerations = []
        
        # Saved because external moment is applied to last mechanism's output
        # So its reaction is applied to output of the mechanism that dirves it
        solution_forces_ = [[],]
        solution_accelerations_ = [[],]
        final_forces_ = []
        #
        #Important to save rotations of links so that stresses can be determined
        absolute_rotations = []
        #
        for mechanism_ in sorting[1:]:
            n_solution = self.mechanisms[mechanism_-1].solution(solutions[self.input_graph[mechanism_]]-self.mechanisms[mechanism_-1].rotation)[inversions[mechanism_-1]]
            n_acceleration = self.mechanisms[mechanism_-1].angular_velocity_angular_acceleration(solutions[self.input_graph[mechanism_]]-self.mechanisms[mechanism_-1].rotation,\
                                                                                                 accelerations[self.input_graph[mechanism_]][2][0], accelerations[self.input_graph[mechanism_]][2][1], inversions[mechanism_-1])
            accelerations[mechanism_] = n_acceleration
            absolute_rotations.append((solutions[self.input_graph[mechanism_]]+self.mechanisms[mechanism_-1].rotation,\
                                            self.mechanisms[mechanism_-1].coupler_rad(solutions[self.input_graph[mechanism_]]-self.mechanisms[mechanism_-1].rotation)[inversions[mechanism_-1]]+self.mechanisms[mechanism_-1].rotation,\
                                            self.mechanisms[mechanism_-1].output_rad(solutions[self.input_graph[mechanism_]]-self.mechanisms[mechanism_-1].rotation)[inversions[mechanism_-1]]+self.mechanisms[mechanism_-1].rotation))
            snapshot.append(n_solution)
            if self.power_graph[mechanism_]:
                solutions[mechanism_] = self.mechanisms[mechanism_-1].output_rad(solutions[self.input_graph[mechanism_]]-self.mechanisms[mechanism_-1].rotation)[inversions[mechanism_-1]]+self.mechanisms[mechanism_-1].rotation
            
            
            #Linear accelerations
            mechanism_analyzed = self.mechanisms[mechanism_-1]
            #Crank linear accelerations
            radius_connection_to_centroid = n_solution[0].connections[mechanism_analyzed.connections[0][0]]-n_solution[0].centroid_vector
            w2 = n_acceleration[0][0]*n_acceleration[0][0]
            ax = radius_connection_to_centroid.x*w2
            ay = radius_connection_to_centroid.y*w2
            
            if n_acceleration[0][1]>0:
                radius_connection_to_centroid.rotate(-pi/2)
            else:
                radius_connection_to_centroid.rotate(pi/2)
            ax+=radius_connection_to_centroid.x*abs(n_acceleration[0][1])
            ay+=radius_connection_to_centroid.y*abs(n_acceleration[0][1])
            
            
            #Coupler and output linear accelerations Mechanism
            if type(mechanism_analyzed) == Mechanism:
                radius_connection_to_centroid = n_solution[0].connections[mechanism_analyzed.connections[0][1]]-n_solution[1].centroid_vector
                w2_cop = n_acceleration[1][0]*n_acceleration[1][0]
                ax_cop = radius_connection_to_centroid.x*w2_cop
                ay_cop = radius_connection_to_centroid.y*w2_cop
                
                if n_acceleration[1][1]>0:
                    radius_connection_to_centroid.rotate(-pi/2)
                else:
                    radius_connection_to_centroid.rotate(pi/2)
                ax_cop+=radius_connection_to_centroid.x*abs(n_acceleration[1][1])
                ay_cop+=radius_connection_to_centroid.y*abs(n_acceleration[1][1])
                
                # Translate relative velocity into absolute
                # The relative velocity is in terms of the connection point from crank not from the centroid, so acceleration for this point needs to be computed
                radius_connection_to_centroid = n_solution[0].connections[mechanism_analyzed.connections[0][0]]-n_solution[0].connections[mechanism_analyzed.connections[0][1]]
                ax_conn = radius_connection_to_centroid.x*w2
                ay_conn = radius_connection_to_centroid.y*w2
                
                if n_acceleration[0][1]>0:
                    radius_connection_to_centroid.rotate(-pi/2)
                else:
                    radius_connection_to_centroid.rotate(pi/2)
                ax_conn+=radius_connection_to_centroid.x*abs(n_acceleration[0][1])
                ay_conn+=radius_connection_to_centroid.y*abs(n_acceleration[0][1])
                
                ax_cop+=ax_conn
                ay_cop+=ay_conn
                
                #Output
                radius_connection_to_centroid = n_solution[3].connections[mechanism_analyzed.connections[3][1]]-n_solution[2].centroid_vector
                w2_out = n_acceleration[2][0]*n_acceleration[2][0]
                ax_out = radius_connection_to_centroid.x*w2_out
                ay_out = radius_connection_to_centroid.y*w2_out
                
                if n_acceleration[2][1]>0:
                    radius_connection_to_centroid.rotate(-pi/2)
                else:
                    radius_connection_to_centroid.rotate(pi/2)
                ax_out+=radius_connection_to_centroid.x*abs(n_acceleration[2][1])
                ay_out+=radius_connection_to_centroid.y*abs(n_acceleration[2][1])
                
                
            
            #Coupler and output linear accelerations SliderCrank
            elif type(mechanism_analyzed) == SliderCrank:
                radius_connection_to_centroid = n_solution[1].connections[mechanism_analyzed.connections[1][1]]-n_solution[1].centroid_vector
                w2_cop = n_acceleration[1][0]*n_acceleration[1][0]
                ax_cop = radius_connection_to_centroid*w2_cop
                ay_cop = radius_connection_to_centroid*w2_cop
                
                if n_acceleration[1][1]>0:
                    radius_connection_to_centroid.rotate(-pi/2)
                else:
                    radius_connection_to_centroid.rotate(pi/2)
                ax_cop+=radius_connection_to_centroid.x*abs(n_acceleration[1][1])
                ay_cop+=radius_connection_to_centroid.y*abs(n_acceleration[1][1])
                
                # Translate relative velocity into absolute
                # Use as reference velocity from output since slider has to be naturally computed and corresponds to the reference point for the SliderCrank coupler
                direction = n_solution[3].connections[mechanism_analyzed.connections[3][1]]-n_solution[3].connections[mechanism_analyzed.connections[3][0]]
                normalize_x = direction.x/((direction.x**2+direction.y**2)**0.5)
                normalize_y = direction.y/((direction.x**2+direction.y**2)**0.5)
                
                ax_out = normalize_x*n_acceleration[2][1]
                ay_out = normalize_y*n_acceleration[2][1]
                ax_cop+=ax_out
                ay_cop+=ay_out
                
            else:
                raise ValueError(f"type '{type(mechanism_analyzed)}' has not defined linear accelerations")
            
            #ax, ay and angular acceleration for each link in each mechanism
            linear_and_angular_accelerations.append([[ax, ay, n_acceleration[0][1]], [ax_cop, ay_cop, n_acceleration[1][1]], [ax_out, ay_out, n_acceleration[2][1]], [0, 0, 0]])
            
            
            force_matrix = np.array([\
                                      [1, 0, 1, 0, 0, 0, 0, 0, 0],\
                                      [0, 1, 0, 1, 0, 0, 0, 0, 0],\
                                      [-(n_solution[0].connections[mechanism_analyzed.connections[0][0]]-n_solution[0].centroid_vector).y, (n_solution[0].connections[mechanism_analyzed.connections[0][0]]-n_solution[0].centroid_vector).x, -(n_solution[0].connections[mechanism_analyzed.connections[0][1]]-n_solution[0].centroid_vector).y, (n_solution[0].connections[mechanism_analyzed.connections[0][1]]-n_solution[0].centroid_vector).x, 0, 0, 0, 0, 1],\
                                      [0, 0, -1, 0, 1, 0, 0, 0, 0],\
                                      [0, 0, 0, -1, 0, 1, 0, 0, 0],\
                                      [0, 0, (n_solution[0].connections[mechanism_analyzed.connections[0][1]]-n_solution[1].centroid_vector).y, -(n_solution[0].connections[mechanism_analyzed.connections[0][1]]-n_solution[1].centroid_vector).x, -(n_solution[1].connections[mechanism_analyzed.connections[1][1]]-n_solution[1].centroid_vector).y, (n_solution[1].connections[mechanism_analyzed.connections[1][1]]-n_solution[1].centroid_vector).x, 0, 0, 0],\
                                      [0, 0, 0, 0, -1, 0, 1, 0, 0],\
                                      [0, 0, 0, 0, 0, -1, 0, 1, 0],\
                                      [0, 0, 0, 0, (n_solution[1].connections[mechanism_analyzed.connections[1][1]]-n_solution[2].centroid_vector).y, -(n_solution[1].connections[mechanism_analyzed.connections[1][1]]-n_solution[2].centroid_vector).x, -(n_solution[2].connections[mechanism_analyzed.connections[2][1]]-n_solution[2].centroid_vector).y, (n_solution[2].connections[mechanism_analyzed.connections[2][1]]-n_solution[2].centroid_vector).x, 0]\
                                    ])
            
            mass_x_accelerations = np.array([\
                                             [n_solution[0].mass*ax],\
                                             [n_solution[0].mass*ay],\
                                             [n_solution[0].moment_inertia_centroid*n_acceleration[0][1]],\
                                             [n_solution[1].mass*ax_cop],\
                                             [n_solution[1].mass*ay_cop],\
                                             [n_solution[1].moment_inertia_centroid*n_acceleration[1][1]],\
                                             [n_solution[2].mass*ax_out],\
                                             [n_solution[2].mass*ay_out],\
                                             [n_solution[2].moment_inertia_centroid*n_acceleration[2][1]]\
                                            ])
            
            solution_accelerations_.append(mass_x_accelerations)
            solution_forces_.append(force_matrix)
            #print(linalg.solve(force_matrix, mass_x_accelerations))
        
        external_moments_crank = []
        external_moments_coupler = []
        
        for i in range(len(self.mechanisms)):
                external_moments_crank.append(0)
        
        if len(external_moments_cranks) == 1:
            external_moments_crank[-1] = external_moments_cranks[0]
        elif len(external_moments_cranks) > 1:
            external_moments_crank = external_moments_cranks
        
        
        for i in range(len(self.mechanisms)):
                external_moments_coupler.append(0)
        
        if len(external_moments_couplers) == 1:
            external_moments_coupler[-1] = external_moments_couplers[0]
        elif len(external_moments_couplers) > 1:
            external_moments_coupler = external_moments_couplers
        
        
        
        for matrix in sorting[::-1][:-1]:
            solution_accelerations_[matrix][-1][0] -= external_moments_crank[matrix-1]
            solution_accelerations_[matrix][-4][0] -= external_moments_coupler[matrix-1]
            solution = linalg.solve(solution_forces_[matrix], solution_accelerations_[matrix])
            final_forces_.append(solution)
            if self.input_graph[matrix] != 0:
                solution_accelerations_[self.input_graph[matrix]][-1][0]-=solution[-1][0]
        
        final_forces_ = final_forces_[::-1]
        final_stresses_ = []
        vonMises_ = []
        locations_ = []
        #Stresses only for the crank of the first mechanism, all others are powered by the output
        include_crank = 0
        current = 0
        for mechanism in snapshot:
            link_ = 0+include_crank
            stresses = []
            location = None
            for link in mechanism[include_crank:-1]:
                max_vonMises = 0
                for i in range(len(link.element_node_locations)):
                    if link.areas[i]<=1e-4:
                        continue
                    forcex = final_forces_[current][link_*2+2][0]
                    forcey = final_forces_[current][link_*2+3][0]
                    move_force = link.element_node_locations[i]-self.mechanisms[current].links[link_].connections[self.mechanisms[current].connections[link_][0]]
                    
                    moment = forcex*move_force.y-forcey*move_force.x+final_forces_[current][-1][0]
                    c = cos(absolute_rotations[current][link_])
                    s = sin(absolute_rotations[current][link_])
                    local_x = forcex*c+forcey*s
                    local_y = -forcex*s+forcey*c
                    
                    moment_stress = moment*link.heights[i]/link.inertias[i]
                    shear_stress = local_y/link.areas[i]
                    normal_stress = local_x/link.areas[i]
                    total_normal_stress = abs(normal_stress)+abs(moment_stress)
                    vonMises = (total_normal_stress*total_normal_stress+3*shear_stress*shear_stress)**0.5
                    if vonMises>max_vonMises:
                        max_vonMises = vonMises
                        stresses = [shear_stress, normal_stress, moment_stress]
                        if (moment_stress > 0 and normal_stress > 0) or (moment_stress < 0 and normal_stress < 0):
                            location = Vector(s*link.heights[i], -c*link.heights[i])+link.element_node_locations[i]
                        else:
                            location = Vector(-s*link.heights[i], c*link.heights[i])+link.element_node_locations[i]
                link_+=1
                final_stresses_.append(stresses)
                vonMises_.append(max_vonMises)
                locations_.append(location)
            include_crank = 1
            current+=1
        return linear_and_angular_accelerations, final_forces_, final_stresses_, vonMises_, locations_, snapshot, sorting
    
    

def topological_sort(mechanisms:List[List[int]]):
    found = []
    def topo_sort(mechanisms:List[List[int]], node_start:int=0):
        """Find the dependencies of mechanisms in a machine"""
        if node_start in found:
            return
        found.append(node_start)
        for node in mechanisms[node_start]:
            topo_sort(mechanisms, node)
        for nnode in range(len(mechanisms)):
            topo_sort(mechanisms, nnode)
    topo_sort(mechanisms)
    return found
    


if __name__ == "__main__":
    a, b = Vector(1, 0), Vector(0, 1)
    print(a)
    a.rotate_angle(180)
    print(a+b)
    print(topological_sort([[1, 2, 3], [4], [5], [], [], []]))    
    