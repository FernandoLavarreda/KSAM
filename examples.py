#Fernando Lavarreda Examples


import geometry as gm


def build_machine():
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
    link4 = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(2, 0)], [bc1, bc2, bc3], 0.0)


    mech = gm.Mechanism(gm.Vector(0, 0), -0.2*gm.pi, [link, link2, link3, link4], ((0, 1), (0, 1), (0, 1), (0, 1)))
    mech2 = mech.copy()
    mech2.rotate(0.2*gm.pi)
    mech2.translate(mech.links[3].connections[mech.connections[3][1]].x, mech.links[3].connections[mech.connections[3][1]].y)

    mech3 = mech.copy()
    mech3.rotate(0.2*gm.pi)
    mech3.translate(mech.links[3].connections[mech.connections[3][1]].x, mech.links[3].connections[mech.connections[3][1]].y)
    mech3.translate(2, 0)

    machine = gm.Machine([mech, mech2, mech3], power_graph=[[1], [2], [3], []])
    return machine


def build_compresor(pistons:int):
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
        p.rotate(distance*i)
        npistons.append(p)
    empty = [[] for i in range(pistons)]
    compresor = gm.Machine(npistons, power_graph=[[i+1 for i in range(pistons)], *empty])
    return compresor


