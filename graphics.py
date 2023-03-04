#Fernando Jose Lavarreda Urizar
#Program to analyze Mechanisms, Graduation Project UVG

import geometry as gm
from time import sleep
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def plot_link(link:gm.Link):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for curve in link.curves:
        ax.plot([vector.x for vector in curve.vectors], [vector.y for vector in curve.vectors])
    miny, maxy = ax.get_ylim()
    minx, maxx = ax.get_xlim()
    
    minimun = min([miny, minx])
    maximum = max([maxy, maxx])
    
    ax.set_xlim([minimun, maximum])
    ax.set_ylim([minimun, maximum])
    
    plt.show()



def plot_mechanism(crank, coupler, output, ground):
    links = [crank, coupler, output, ground]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    
    for link in links:
        for curve in link.curves:
            ax.plot([vector.x for vector in curve.vectors], [vector.y for vector in curve.vectors])
    miny, maxy = ax.get_ylim()
    minx, maxx = ax.get_xlim()
    plt.show()


def plot_rotation(mechanism:gm.Mechanism, frames:int, inversion:int=0):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    s1 = mechanism.solution(0)[inversion]
    
    lines = []
    for link in s1:
        lines.append([])
        for curve in link.curves:
            lines[-1].append(*ax.plot([vector.x for vector in curve.vectors], [vector.y for vector in curve.vectors]))
    
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
    plt.show()





if __name__ == "__main__":
    #radii 
    c1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20)**2) for x in range(11)])
    c2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20-1)**2) for x in range(10, 21)])
    c3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)])
    
    hc1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/40, 1+(0.25-(x/40-0.5)**2)**0.5) for x in range(41)])
    hc2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/40, -1-(0.25-(x/40-0.5)**2)**0.5) for x in range(41)])
    jcurve = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 1), gm.Vector(0, -1)])
    jcurve2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(1, 1), gm.Vector(1, -1)])
    
    
    bc1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, -(x/20)**2) for x in range(21)])
    bc2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, -(x/20-2)**2) for x in range(20, 41)])
    bc3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(2, 0)])
    
    
    link = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)], [c1, c2, c3], 0.0)
    link2 = gm.Link(gm.Vector(0, 0), [gm.Vector(0.5, 1.25), gm.Vector(0.5, -1.25)], [hc1.copy(), hc2.copy(), jcurve.copy(), jcurve2.copy()], 0.0)
    link3 = gm.Link(gm.Vector(0, 0), [gm.Vector(0.5, 1.25), gm.Vector(0.5, -1.25)], [hc1, hc2, jcurve, jcurve2], 0.0)
    link4 = gm.Link(gm.Vector(0, 0), [gm.Vector(0, -0.2), gm.Vector(2, -0.2)], [bc1, bc2, bc3], 0.0)
    
    
    mech = gm.Mechanism(gm.Vector(0, 0), -0.2*gm.pi, [link, link2, link3, link4], ((0, 1), (0, 1), (0, 1), (0, 1)))
    #plot_link(mech.links[1])
    #plot_link(mech.solution(0*gm.pi)[1][1])
    #plot_link(mech.solution(0*gm.pi)[1][0])
    #plot_mechanism(*mech.solution(0.2*gm.pi)[1])
    plot_rotation(mech, frames=100, inversion=1)




