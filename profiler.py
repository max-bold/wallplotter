from typing import Tuple
from math import sqrt, acos


class point(object):
    def __init__(
            self,
            x: float = None,
            y: float = None,
            z: float = None,
            e: float = None) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.e = e


class line(object):
    def __init__(self, a: point, b: point, vel: float) -> None:
        self.a = a
        self.b = b
        self.vel = vel

    def length(self) -> float:
        x = self.a.x-self.b.x
        y = self.a.y-self.b.y
        z = self.a.z-self.b.z
        e = self.a.e-self.b.e
        return sqrt(x**2+y**2+z**2+e**2)

    def length3D(self) -> float:
        x = self.a.x-self.b.x
        y = self.a.y-self.b.y
        z = self.a.z-self.b.z
        return sqrt(x**2+y**2+z**2)


def smoother(a: point, b: point, c: point, d: float):
    angle = acos(())
