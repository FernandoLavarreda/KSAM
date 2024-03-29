#Fernando Jose Lavarreda Urizar
#Program to analyze Mechanisms, Graduation Project UVG, Free & Open Source


if __name__ == "__main__":
    import os
    import sys
    parent = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(parent)

try:
    from mechanisms import geometry as gm
except ImportError:
    from ..mechanisms import geometry as gm
    

def build_machine():
    c1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20)**2) for x in range(11)], function=gm.Function(start=0, end=0.5, process=lambda x: x**2))
    c2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20-1)**2) for x in range(10, 21)], function=gm.Function(start=0.5, end=1, process=lambda x: (x-1)**2))
    c3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)], function=gm.Function(start=0, end=1, process=lambda x: 0))

    hc1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/40, 1+(0.25-(x/40-0.5)**2)**0.5) for x in range(41)], function=gm.Function(start=0, end=1, process=lambda x: 1+((0.25-(x-0.5)**2))**0.5))
    hc2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/40, -1-(0.25-(x/40-0.5)**2)**0.5) for x in range(41)], function=gm.Function(start=0, end=1, process=lambda x: -1-((0.25-(x-0.5)**2))**0.5))
    jcurve = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 1), gm.Vector(0, -1)])
    jcurve2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(1, 1), gm.Vector(1, -1)])


    bc1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, -(x/20)**2) for x in range(21)], function=gm.Function(start=0, end=1, process=lambda x: -x**2))
    bc2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, -(x/20-2)**2) for x in range(20, 41)], function=gm.Function(start=1, end=2, process=lambda x: -(x-2)**2))
    bc3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(2, 0)], function=gm.Function(start=0, end=2, process=lambda x: 0))


    link = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)], [c1, c2, c3], thickness=0.1, name="crank machine")
    link2 = gm.Link(gm.Vector(0, 0), [gm.Vector(0.5, 1.25), gm.Vector(0.5, -1.25)], [hc1.copy(), hc2.copy(), jcurve.copy(), jcurve2.copy()], thickness=0.1, name="coupler machine")
    link3 = gm.Link(gm.Vector(0, 0), [gm.Vector(0.5, 1.25), gm.Vector(0.5, -1.25)], [hc1, hc2, jcurve, jcurve2], thickness=0.1, name="output machine")
    link4 = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(2, 0)], [bc1, bc2, bc3], thickness=0.1, name="ground machine")
    
    #Centroid calculations
    link.set_lims([0, 1], 1)
    link.set_lims([2,], 0)
    
    link2.set_lims([0,], 1)
    link2.set_lims([1,], 0)
    
    link3.set_lims([0,], 1)
    link3.set_lims([1,], 0)
    
    link4.set_lims([2,], 1)
    link4.set_lims([0,1], 0)
    
    mech = gm.Mechanism(gm.Vector(0, 0), -0.2*gm.pi, [link, link2, link3, link4], ((0, 1), (0, 1), (0, 1), (0, 1)), stress_analysis=True, dx=1e-3, density=1)
    
    mech2 = mech.copy()
    mech2.rotate(0.2*gm.pi)
    mech3 = mech.copy()
    mech3.rotate(0.2*gm.pi)
    mech.name = "machine 1"
    mech2.name = "machine 2" 
    mech3.name = "machine 3"
    machine = gm.Machine([mech, mech2, mech3], power_graph=[[1], [2], [3], []], name="Machine", auto_adjust=True)
    return machine


def build_compresor(pistons:int):
    gg = gm.Curve(gm.Vector(0, 0), [gm.Vector(0,0,),])
    ground = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0)], [gg,], 0.0, name="ground compressor")
    half_circle = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (4-(x/20)**2)**0.5) for x in range(-40, 41)])
    half_circle.rotate(gm.pi/2)
    half_circle2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/80, (0.5-(x/80)**2)**0.5) for x in range(-36, 37)])
    half_circle2.rotate(-gm.pi/2)
    half_circle2.translate(4, 0)
    line_down = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 2), gm.Vector(4.5, 0.45)])
    line_up = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, -2), gm.Vector(4.5, -0.45)])
    crank = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(4, 0)], [half_circle, line_down, line_up, half_circle2], 0.0, name="crank compressor")
    
    half_circle3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/80, (0.25-(x/80)**2)**0.5) for x in range(-40, 41)])
    half_circle3.rotate(gm.pi/2)
    line_down2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0.5), gm.Vector(12, 0)])
    line_up2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, -0.5), gm.Vector(12, 0)])
    coupler = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(12, 0)], [half_circle3, line_down2, line_up2], 0.0, name="coupler compressor")
    
    side1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)])
    side2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(0, 2)])
    side3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 2), gm.Vector(1, 2)])
    side4 = gm.Curve(gm.Vector(0, 0), [gm.Vector(1, 0), gm.Vector(1, 2)])
    slider = gm.Link(gm.Vector(0, 0), [gm.Vector(0.5, 1)], [side1, side2, side3, side4], 0.0, name="compressor slider")
    piston_1 = gm.SliderCrank(gm.Vector(0, 0), 0, [crank, coupler, slider, ground], ((0, 1), (0, 1), (0,), (0,)))
    
    if pistons%2:
        above_x_axis = (pistons+1)//2
        phase_dif = (gm.pi-(above_x_axis-1)*2*gm.pi/pistons)/2
    else:
        phase_dif = 0
    
    piston_1.rotate(phase_dif)
    distance = 2*gm.pi/pistons
    npistons = []
    for i in range(pistons):
        p = piston_1.copy()
        p.name = "piston "+str(i+1)
        p.rotate(distance*i)
        npistons.append(p)
    empty = [[] for i in range(pistons)]
    compresor = gm.Machine(npistons, power_graph=[[i+1 for i in range(pistons)], *empty], name=f"Compresor {pistons} pistons")
    return compresor


def build_vline():
    gg = gm.Curve(gm.Vector(0, 0), [gm.Vector(0,0,),])
    ground = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0)], [gg,], 0.0)
    half_circle = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (4-(x/20)**2)**0.5) for x in range(-40, 41)])
    half_circle.rotate(gm.pi/2)
    half_circle2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/80, (0.5-(x/80)**2)**0.5) for x in range(-36, 37)])
    half_circle2.rotate(-gm.pi/2)
    half_circle2.translate(4, 0)
    line_down = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 2), gm.Vector(4.5, 0.45)])
    line_up = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, -2), gm.Vector(4.5, -0.45)])
    crank = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(4, 0)], [half_circle, line_down, line_up, half_circle2], 0.0)
    
    half_circle3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/80, (0.25-(x/80)**2)**0.5) for x in range(-40, 41)])
    half_circle3.rotate(gm.pi/2)
    line_down2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0.5), gm.Vector(12, 0)])
    line_up2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, -0.5), gm.Vector(12, 0)])
    coupler = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(12, 0)], [half_circle3, line_down2, line_up2], 0.0)
    
    side1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)])
    side2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(0, 2)])
    side3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 2), gm.Vector(1, 2)])
    side4 = gm.Curve(gm.Vector(0, 0), [gm.Vector(1, 0), gm.Vector(1, 2)])
    slider = gm.Link(gm.Vector(0, 0), [gm.Vector(0.5, 1)], [side1, side2, side3, side4], 0.0)
    piston_1 = gm.SliderCrank(gm.Vector(0, 0), 0, [crank, coupler, slider, ground], ((0, 1), (0, 1), (0,), (0,)), name="v-piston-1")
    piston_1.rotate(gm.pi/4)
    piston_2 = piston_1.copy()
    piston_2.rotate(gm.pi/2)
    piston_2.name = "v-piston-2"
    vline = gm.Machine([piston_1, piston_2], power_graph=[[1, 2], [], []], name=f"V-engine")
    return vline


def build_double_crank(pistons:int):
    compresor = build_compresor(pistons)
    half_circle = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (4-(x/20)**2)**0.5) for x in range(-40, 41)])
    half_circle.rotate(gm.pi/2)
    half_circle2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/80, (0.5-(x/80)**2)**0.5) for x in range(-36, 37)])
    half_circle2.rotate(-gm.pi/2)
    half_circle2.translate(4, 0)
    line_down = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 2), gm.Vector(4.5, 0.45)])
    line_up = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, -2), gm.Vector(4.5, -0.45)])
    crank = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(4, 0)], [half_circle, line_down, line_up, half_circle2], 0.0)
    output = crank.copy()
    
    output.connections = output.connections[::-1]
    radii_1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/10, -(6.25-(x/10)**2)**0.5) for x in range(-25, 26)])
    radii_2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/10, -(12.25-(x/10)**2)**0.5) for x in range(-35, 36)])
    
    r_1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/10, (0.25-(x/10)**2)**0.5) for x in range(-5, 6)])
    r_2 = r_1.copy()
    r_1.translate(-3, 0)
    r_2.translate(3, 0)
    coupler = gm.Link(gm.Vector(0, 0), [gm.Vector(-3, 0), gm.Vector(3, 0)], [radii_1, radii_2, r_1, r_2], 0.0)
    
    horizontal_1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0.5, 1), gm.Vector(1.5, 1)])
    horizontal_2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(2, 0)])
    diagonal_1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(0.5, 1)])
    diagonal_2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(1.5, 1), gm.Vector(2, 0)])
    temp_link = gm.Link(gm.Vector(0, 0), [gm.Vector(1, 0.5), ], [diagonal_1, horizontal_1, diagonal_2, horizontal_2], 0.0)
    temp_link_2 = temp_link.copy()
    temp_link_2.translate(6, 0)
    ground = gm.Link(gm.Vector(0, 0), [temp_link.connections[0], temp_link_2.connections[0]], temp_link.curves[:]+temp_link_2.curves[:], 0.0)
    
    
    power_mech = gm.Mechanism(gm.Vector(0, 0), 0, [crank, coupler, output, ground], ((0, 1), (0, 1), (0, 1), (0, 1)), name="Externally powered compresor")
    empty = [[] for i in range(pistons)]
    powered = [i+1 for i in range(1, pistons+1)]
    powered_compresor = gm.Machine([power_mech, *compresor.mechanisms[:]], power_graph=[[1,], powered, *empty], name=f"Powered compresor", auto_adjust=True)
    return powered_compresor


def build_mechanism():
    print("Delete build_mechanism....")
    gg = gm.Curve(gm.Vector(0, 0), [gm.Vector(0,0,),])
    ground = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0)], [gg,], 0.0, name="ground compressor")
    half_circle = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (4-(x/20)**2)**0.5) for x in range(-40, 41)])
    half_circle.rotate(gm.pi/2)
    half_circle2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/80, (0.5-(x/80)**2)**0.5) for x in range(-36, 37)])
    half_circle2.rotate(-gm.pi/2)
    half_circle2.translate(4, 0)
    line_down = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 2), gm.Vector(4.5, 0.45)])
    line_up = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, -2), gm.Vector(4.5, -0.45)])
    crank = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(4, 0)], [half_circle, line_down, line_up, half_circle2], 0.0, name="crank compressor")
    
    half_circle3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/80, (0.25-(x/80)**2)**0.5) for x in range(-40, 41)])
    half_circle3.rotate(gm.pi/2)
    line_down2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0.5), gm.Vector(12, 0)])
    line_up2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, -0.5), gm.Vector(12, 0)])
    coupler = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(12, 0)], [half_circle3, line_down2, line_up2], 0.0, name="coupler compressor")
    
    side1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)])
    side2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(0, 2)])
    side3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 2), gm.Vector(1, 2)])
    side4 = gm.Curve(gm.Vector(0, 0), [gm.Vector(1, 0), gm.Vector(1, 2)])
    slider = gm.Link(gm.Vector(0, 0), [gm.Vector(0.5, 1)], [side1, side2, side3, side4], 0.0, name="compressor slider")
    piston_1 = gm.SliderCrank(gm.Vector(0, 0), 0, [crank, coupler, slider, ground], ((0, 1), (0, 1), (0,), (0,)))
    return piston_1


if __name__ == "__main__":
    #Test forces, speeds
    
    if '1' in sys.argv:
        print("Calculting centroid, mass and moment of inertia from 'machine' crank")
        c1 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20)**2) for x in range(11)], function=gm.Function(start=0, end=0.5, process=lambda x: x**2))
        c2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20-1)**2) for x in range(10, 21)], function=gm.Function(start=0.5, end=1, process=lambda x: (x-1)**2))
        c3 = gm.Curve(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)], function=gm.Function(start=0, end=1, process=lambda x: 0))
        link = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)], [c1, c2, c3], 1)
        link.set_lims([0, 1], 1)
        link.set_lims([2,], 0)
        print(link.centroid(dx=1e-4, density=1e3))
        print("Mass:", link.mass)
        print("Moment inertia:", link.moment_inertia_centroid)
    
    if '2' in sys.argv:
        print("Calculting centroid, mass and moment of inertia from disc")
        half_circle = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20)**2) for x in range(40)], function=gm.Function(start=0, end=2, process=lambda x: (1-(x-1)**2)**0.5))
        half_circle2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20-1)**2) for x in range(10, 21)], function=gm.Function(start=0, end=2, process=lambda x: -(1-(x-1)**2)**0.5))
        link = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)], [half_circle, half_circle2], 1)
        link.set_lims([0,], 1)
        link.set_lims([1,], 0)
        print(link.centroid(dx=1e-4, density=1e3))
        print("Mass:", link.mass)
        print("Moment inertia:", link.moment_inertia_centroid)
    
    if '3' in sys.argv:
        print("Calculating accelerations for 'machine'")
        machine = build_machine()
        accelerations, forces, stresses, vonMises, locations, _, _ = machine.solution_kinetics(1.8*gm.pi, 0.2, 1, [1,], pattern=1)
        print(f"Accelerations: {accelerations}\nForces: {forces}\nStresses: {stresses}\nvon Mises: {vonMises}")
        print("Locations:")
        for i in locations:
            print(i)
    
    

