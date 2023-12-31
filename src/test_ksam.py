#!../venv/bin/python3.11
import pytest
from math import pi
from .mechanisms import geometry as gm
from .examples import examples as ex


def test_centroid():
    """Assert implementations to obtain location of centroid of moment of inertia are correct"""
    half_circle = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20)**2) for x in range(40)], function=gm.Function(start=0, end=2, process=lambda x: (1-(x-1)**2)**0.5))
    half_circle2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20-1)**2) for x in range(10, 21)], function=gm.Function(start=0, end=2, process=lambda x: -(1-(x-1)**2)**0.5))
    link = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)], [half_circle, half_circle2], 1)
    link.set_lims([0,], 1)
    link.set_lims([1,], 0)
    centroid_vec = link.centroid(dx=1e-4, density=1e3)
    assert 1 == pytest.approx(centroid_vec.x) 
    assert 0 == pytest.approx(centroid_vec.y) 


def test_mass():
    """Test if volume of Link is accurately computed"""
    half_circle = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20)**2) for x in range(40)], function=gm.Function(start=0, end=2, process=lambda x: (1-(x-1)**2)**0.5))
    half_circle2 = gm.Curve(gm.Vector(0, 0), [gm.Vector(x/20, (x/20-1)**2) for x in range(10, 21)], function=gm.Function(start=0, end=2, process=lambda x: -(1-(x-1)**2)**0.5))
    link = gm.Link(gm.Vector(0, 0), [gm.Vector(0, 0), gm.Vector(1, 0)], [half_circle, half_circle2], 1)
    link.set_lims([0,], 1)
    link.set_lims([1,], 0)
    link.centroid(dx=1e-4, density=1e3)
    assert 1e3*pi == pytest.approx(link.mass)


def test_mechanism():
    """Test cinematics of slider mechanism"""
    piston = ex.build_mechanism()
    d = piston.output_rad(0, piston.coupler_rad(0)[1])
    assert d == pytest.approx(piston.a+piston.b)

