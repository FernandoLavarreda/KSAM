#Fernando Jose Lavarreda Urizar
#Program to analyze Mechanisms, Graduation Project UVG


from typing import List, Tuple
from math import sin, cos, pi, sqrt, atan



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
    
    
    def __str__(self):
        return f"Vector: \nx: {self.x}\ny: {self.y}"


def vector_length(a:Vector, b:Vector):
    """Return the distance between two vectors"""
    return sqrt((b.x-a.x)**2+(b.y-a.y)**2)


class Curve:
    def __init__(self, origin:Vector, vectors:List[Vector]):
        """Series of Vectors to create a profile
           origin: Absolute position where the start of the Curve is locateds"""
        self.vectors = vectors
        self.origin = origin
    
    
    def rotate(self, angle:float):
        for v in self.vectors:
            v.rotate(angle)
    
    
    def rotate_angle(self, angle:float):
        self.rotate(angle_rad(angle))
    
    
    def translate(self, x:float, y:float)->Vector:
        for v in self.vectors:
            v.translate(x, y)
    
    
    def absolute(self):
        return Curve(self.origin, [v+self.origin for v in self.vectors])
    


class Link:
    def __init__(self, origin:Vector, connections:List[Vector], curves:List[Curve], thickness:float):
        """A link is a segment of a mechanim for which the position and stress are desired
           origin: Absolute position where the start of the Link is located
           connections: Vectors where another link may be connected to create a mechanim"""
        self.origin = origin
        self.connections = connections
        self.curves = curves
        self.thickness = thickness
    
    
    def rotate(self, angle:float):
        self.rotate(angle_rad(angle))
    
    
    def rotate_angle(self, angle:float):
        for curve in self.curves:
            curve.rotate_angle(angle)
    
    
    def translate(self, x:float, y:float):
        for curve in self.curves:
            curve.translate(x, y)
    
    
    def absolute(self):
        return Link(self.origin, [conn+self.origin for conn in self.connections], [c.absolute() for c in self.curves], thickness)
    
    
    def length(self, a, b):
        """Get the length between two connection points in the Link, 0 based"""
        assert a < len(self.connections), "a argument is out of bounds"
        assert b < len(self.connections), "b argument is out of bounds"
        return vector_length(self.connections[a], self.connections[b])



class Mechanism:
    def __init__(self, origin:Vector, links:List[Link], connections:List[Tuple[int, int]]):
        """Representation of 4 bar mechanism, must be ordered as follows: a (crank), b (coupler), c (output), d (bench/ground)
           connections: numbers indicating the connection points from the links to use"""
        assert len(connections) == len(links), "Missmatch between connections and links"
        assert len(links) == 4, "Can only solve for 4 bar mechanism"
        self.origin = origin
        self.links = links
        self.connections = connections
        
        self.a = links[0].length(connections[0][0], connections[0][1])
        self.b = links[1].length(connections[1][0], connections[1][1])
        self.c = links[2].length(connections[2][0], connections[2][1])
        self.d = links[3].length(connections[3][0], connections[3][1])
        self.k1 = self.d/self.a
        self.k2 = self.d/self.c
        self.k3 = (self.a*self.a-self.b*self.b+self.c*self.c+self.d*self.d)/(2*self.a*self.c)
        self.k4 = self.d/self.b
        self.k5 = (self.c*self.c-self.d*self.d-self.a*self.a-self.b*self.b)/(2*self.a*self.b)
    
    
    def output_rad(self, input_rad):
        """input_rad: crank angle relative to ground in rads
        raise a ValueError if the crank can't be placed in that position"""
        A = cos(input_rad)-self.k1-self.k2*cos(input_rad)+self.k3
        B = -2*sin(input_rad)
        C = self.k1-(self.k2+1)*cos(input_rad)+self.k3
        
        try:
            solution_a = 2*atan(-B+sqrt(B*B-4*A*C)/2/A)
            solution_b = 2*atan(-B-sqrt(B*B-4*A*C)/2/A)
        except ValueError:
            raise ValueError("Crank can't be put in that position")
        
        return solution_a, solution_b
    
    
    def output_angle(self, input_angle):
        """input_angle: crank angle relative to ground in degrees
        raise a ValueError if the crank can't be placed in that position"""
        a, b = output_rad(angle_rad(input_angle))
        return rad_angle(a), rad_angle(b)
    
    
    def coupler_rad(self, input_rad):
        """input_rad: crank angle relative to ground in rads
        raise a ValueError if the crank can't be placed in that position"""
        D = cos(input_rad)-self.k1+self.k4*cos(input_rad)+self.k5
        E = -2*sin(input_rad)
        F = self.k1+(self.k4-1)*cos(input_rad)+self.k5
        
        try:
            solution_a = 2*atan(-E+sqrt(E*E-4*D*F)/2/D)
            solution_b = 2*atan(-E-sqrt(E*E-4*D*F)/2/D)
        except ValueError:
            raise ValueError("Crank can't be put in that position")
        
        return solution_a, solution_b
    
    
    def coupler_angle(self, input_angle):
        """input_angle: crank angle relative to ground in degrees
        raise a ValueError if the crank can't be placed in that position"""
        a, b = coupler_rad(angle_rad(input_angle))
        return rad_angle(a), rad_angle(b)


class Machine:
    def __init__(self, mechanisms:List[Mechanism]):
        """A machine is defined here as one or more 4-bar mechanisms connected"""
        self.mechanisms = mechanisms


if __name__ == "__main__":
    a, b = Vector(1, 0), Vector(0, 1)
    print(a)
    a.rotate_angle(180)
    print(a+b)






