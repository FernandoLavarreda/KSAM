#Fernando Jose Lavarreda Urizar
#Program to analyze Mechanisms, Graduation Project UVG


from typing import List, Tuple, Mapping
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
        return f"Vector: \nx: {self.x}\ny: {self.y}"
    
    
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



class Curve:
    def __init__(self, origin:Vector, vectors:List[Vector], name="", functions=""):
        """Series of Vectors to create a profile
           origin: Absolute position where the start of the Curve is located"""
        self.vectors = vectors
        self.origin = origin
        self.name = name
        self.functions = functions
    
    
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
    
    
    def copy(self):
        return Curve(self.origin.copy(), [v.copy() for v in self.vectors], self.name, self.functions)



class Link:
    def __init__(self, origin:Vector, connections:List[Vector], curves:List[Curve], thickness:float, name=""):
        """A link is a segment of a mechanism for which the position and stress are desired
           origin: Absolute position where the start of the Link is located
           connections: Vectors where another link may be connected to create a mechanism"""
        self.origin = origin
        self.connections = connections
        self.curves = curves
        self.thickness = thickness
        self.name = name
        self.translation = Vector(0, 0)
        self.rotation = 0
    
    
    def rotate(self, angle:float):
        for curve in self.curves:
            curve.rotate(angle)
        
        for conn in self.connections:
            conn.rotate(angle)
        self.rotation+=angle
    
    
    def rotate_angle(self, angle:float):
        self.rotate(angle_rad(angle))
    
    
    def translate(self, x:float, y:float):
        for curve in self.curves:
            curve.translate(x, y)
        
        for conn in self.connections:
            conn.translate(x, y)
        self.translation+=Vector(x, y)
    
    
    def absolute(self):
        return Link(self.origin, [conn+self.origin for conn in self.connections], [c.absolute() for c in self.curves], thickness)
    
    
    def length(self, a, b):
        """Get the length between two connection points in the Link, 0 based"""
        assert a < len(self.connections), "a argument is out of bounds"
        assert b < len(self.connections), "b argument is out of bounds"
        return vector_length(self.connections[a], self.connections[b])
    
    
    def copy(self):
        return Link(self.origin.copy(), [conn.copy() for conn in self.connections], [c.copy() for c in self.curves], self.thickness, self.name)



class Mechanism:
    def __init__(self, origin:Vector, rotation:float, links:List[Link], connections:List[Tuple[int, int]], init=True, name=""):
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
            else:
                self.links[i].translate(-self.links[i].connections[self.connections[i][0]].x, -self.links[i].connections[self.connections[i][0]].y)
                self.links[i].rotate(-vector_angle(self.links[i].connections[self.connections[i][0]], self.links[i].connections[self.connections[i][1]])+self.rotation)
    
    
    def copy(self):
        mechanism = Mechanism(self.origin.copy(), self.rotation, links=self.links, connections=[i for i in self.connections], init=False, name=self.name)
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
            raise ValueError("Crank can't be put in that position")
        
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
    def __init__(self, origin:Vector, rotation:float, links:List[Link], connections:List[Tuple[int, int]], offset:float=0, init=True, name=""):
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
        
        
        #Ground optional
        if len(links) == 3:
            gg = Curve(gm.Vector(0, 0), [gm.Vector(0,0,),])
            self.links.append(Link(gm.Vector(0, 0), [gm.Vector(0, 0)], [gg,], 0.0))
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
        mv_out = coupler.connections[self.connections[0][1]]-output.connections[self.connections[0][0]]
        mv_out2 = coupler2.connections[self.connections[0][1]]-output2.connections[self.connections[0][0]]
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




