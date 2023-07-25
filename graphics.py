#Fernando Jose Lavarreda Urizar
#Program to analyze Mechanisms, Graduation Project UVG

import geometry as gm
from time import sleep
from typing import List
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation


def plot_link(link:gm.Link, axes:Axes=None, show_connections:bool=False, grid:bool=False, resize:bool=False, color=""):
    if axes:
        ax = axes
    else:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    
    if color:
        for curve in link.curves:
            ax.plot([vector.x for vector in curve.vectors], [vector.y for vector in curve.vectors], color=color)
    else:
        for curve in link.curves:
            ax.plot([vector.x for vector in curve.vectors], [vector.y for vector in curve.vectors])
    
    if show_connections:
        ax.scatter([vector.x for vector in link.connections], [vector.y for vector in link.connections], color="red")
    
    if resize:
        miny, maxy = ax.get_ylim()
        minx, maxx = ax.get_xlim()
        
        minimun = min([miny, minx])
        maximum = max([maxy, maxx])
        
        ax.set_xlim([minimun, maximum])
        ax.set_ylim([minimun, maximum])
    ax.grid(visible=grid)
    
    if not grid:
        ax.set_xticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_yticklabels([])
    
    if not axes:
        plt.show()



def plot_mechanism(crank:gm.Link, coupler:gm.Link, output:gm.Link, ground:gm.Link, axes:Axes=None, colors:List[str]=["red", "purple", "green", "orange", "blue", "black", "yellow"]):
    links = [crank, coupler, output, ground]
    
    if axes:
        ax = axes
    else:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    
    color=0
    for link in links:
        for curve in link.curves:
            ax.plot([vector.x for vector in curve.vectors], [vector.y for vector in curve.vectors], color=colors[color%len(colors)])
        color+=1
    miny, maxy = ax.get_ylim()
    minx, maxx = ax.get_xlim()
    
    minimun = min([miny, minx])
    maximum = max([maxy, maxx])
    
    ax.set_xlim([minimun, maximum])
    ax.set_ylim([minimun, maximum])
    
    if not axes:
        plt.show()


def plot_machine(mechanisms:List[List[gm.Link]], axes:Axes=None, colors:List[str]=["red", "purple", "green", "orange", "blue", "black", "yellow"], mass_center:bool=False, max_stress:List[gm.Vector]=[]):
    if mass_center:
        for jindex, m in enumerate(mechanisms):
            for index, l in enumerate(m):
                assert l.centroid_vector, f"Missing centroid for link {index} in mechanism {jindex}"
    
    if axes:
        ax = axes
    else:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    
    color = 0
    omit_crank = 0
    for mechanism in mechanisms:
        for link in mechanism[omit_crank:]:
            for curve in link.curves:
                ax.plot([vector.x for vector in curve.vectors], [vector.y for vector in curve.vectors], color=colors[color%len(colors)])
            color+=1
            if mass_center:
                ax.scatter([link.centroid_vector.x,], [link.centroid_vector.y], color='red')
            if max_stress:
                ax.scatter([v.x for v in max_stress], [v.y for v in max_stress], color="lime")
        omit_crank= 1
    miny, maxy = ax.get_ylim()
    minx, maxx = ax.get_xlim()
    
    if not axes:
        plt.show()


def plot_rotation_mech(mechanism:gm.Mechanism, frames:int, inversion:int=0, colors:List[str]=["red", "purple", "green", "orange", "blue", "black", "yellow"], axes:Axes=None, fig:Figure=None):
    assert (axes == None and fig == None) or (axes != None and fig != None), "Assign both axes and figure or none"
    if axes:
        ax = axes
    else:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    s1 = mechanism.solution(0)[inversion]
    
    ax.set_xlim([-mechanism.size+mechanism.location().x, mechanism.size+mechanism.location().x])
    ax.set_ylim([-mechanism.size+mechanism.location().y, mechanism.size+mechanism.location().y])
    
    lines = []
    color = 0
    for link in s1:
        lines.append([])
        for curve in link.curves:
            lines[-1].append(*ax.plot([vector.x for vector in curve.vectors], [vector.y for vector in curve.vectors], color=colors[color%len(colors)]))
        color+=1
    
    def animate(i):
        radian = 2*gm.pi*i/frames
        solution = mechanism.solution(radian)[inversion]
        for link in range(4):
            counter = 0
            for curve in solution[link].curves:
                lines[link][counter].set_data([v.x for v in curve.vectors], [v.y for v in curve.vectors])
                counter+=1
        ret = []
        for ll in lines:
            for cc in ll:
                ret.append(cc)
        return ret
    
    anim = FuncAnimation(fig, animate, frames=frames, interval=20, blit=True)
    
    if not axes:
        plt.show()
    else:
        return anim


def plot_rotation_mach(machine:gm.Machine, frames:int, inversion:int=0, lims=[[-1.5, 7], [-2.5, 4]], colors:List[str]=["red", "purple", "green", "orange", "blue", "black", "yellow"],\
                       axes:Axes=None, fig:Figure=None, animation_limits=(0, gm.pi*2), invert:bool=False, mass_center:bool=False, save=""):
    """
    Inversion can be either 0 for 0s list a 1 for 1s list or a list indicating the inversion for each mechanism
    """
    assert (axes == None and fig == None) or (axes != None and fig != None), "Assign both axes and figure or none"
    if axes:
        ax = axes
    else:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    
    starter_sol = machine.solution(0, inversion)
    
    ax.set_xlim(lims[0])
    ax.set_ylim(lims[1])
    
    
    #Important to skip crank for all mechanisms except input one
    lines = []
    current_mech = 0
    current_link = 0
    color = 0
    centroids = []
    for mechanism_ in starter_sol:
        lines.append([])
        current_link = 0
        if starter_sol[current_mech][0].centroid_vector and mass_center:
            if current_mech == 0:
                inputs_ = 0
            else:
                inputs_ = 1
            centroids.append(ax.scatter([link.centroid_vector.x for link in starter_sol[current_mech][inputs_:]], [link.centroid_vector.y for link in starter_sol[current_mech][inputs_:]], color="red"))
        else:
            centroids.append(None)
        for link_ in mechanism_:
            lines[-1].append([])
            if not(current_mech != 0 and current_link == 0):
                for curve_ in link_.curves:
                    lines[-1][-1].append(*ax.plot([vector.x for vector in curve_.vectors], [vector.y for vector in curve_.vectors], color=colors[color%len(colors)]))
            current_link+=1
            color+=1
        current_mech+=1
    
    
    def animate(i):
        if invert:
            if i >= frames/2:
                radian = animation_limits[1]-(animation_limits[1]-animation_limits[0])*(i/frames-0.5)*2
            else:
                radian = (animation_limits[1]-animation_limits[0])*2*i/frames+animation_limits[0]
        else:
            radian = (animation_limits[1]-animation_limits[0])*i/frames+animation_limits[0]
        solution = machine.solution(radian, inversion)
        for mechanism in range(len(lines)):
            for link in range(len(lines[mechanism])):
                counter = 0
                if mechanism != 0 and link == 0:
                    continue
                for curve in solution[mechanism][link].curves:
                    lines[mechanism][link][counter].set_data([v.x for v in curve.vectors], [v.y for v in curve.vectors])
                    counter+=1
        
        ret = []
        for mech in lines:
            for link in mech:
                for curve in link:
                    ret.append(curve)
        
        for mechanism__ in range(len(solution)):
            if centroids[mechanism__]:
                if mechanism__ == 0:
                    inputs_ = 0
                else:
                    inputs_ = 1
                centroids[mechanism__].set_offsets([(link.centroid_vector.x, link.centroid_vector.y) for link in solution[mechanism__][inputs_:]])
                ret.append(centroids[mechanism__])
        return ret
    
    anim = FuncAnimation(fig, animate, frames=frames, interval=20, blit=True)
    
    if save:
        anim.save(save)
    
    if not axes:
        plt.show()
    else:
        return anim




if __name__ == "__main__":
    import sys
    import examples
    
    if '1' in sys.argv:
        machine = examples.build_machine()
        plot_rotation_mach(machine, frames=100, inversion=1, mass_center=True)
    
    if '2' in sys.argv:
        compresor = examples.build_compresor(5)
        plot_rotation_mach(compresor, frames=100, inversion=1, lims=[[-17, 17], [-17, 17]], save="")
    
    if '3' in sys.argv:
        powered = examples.build_double_crank(5)
        plot_rotation_mach(powered, frames=200, inversion=[0, 1, 1, 1, 1, 1], lims=[[-12, 24], [-17, 17]], save="")
    
    
    if '4' in sys.argv:
        machine = examples.build_machine()
        plot_machine(machine.solution(1.8*gm.pi, pattern=1), mass_center=True)
    


