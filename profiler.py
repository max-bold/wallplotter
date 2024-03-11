from typing import Tuple
from math import sqrt, acos, copysign
from numpy import linspace
from time import time, sleep


# from matplotlib import plot


class point(object):
    def __init__(
        self, x: float = None, y: float = None, z: float = None, e: float = None
    ) -> None:
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
        x = self.a.x - self.b.x
        y = self.a.y - self.b.y
        z = self.a.z - self.b.z
        e = self.a.e - self.b.e
        return sqrt(x**2 + y**2 + z**2 + e**2)

    def length3D(self) -> float:
        x = self.a.x - self.b.x
        y = self.a.y - self.b.y
        z = self.a.z - self.b.z
        return sqrt(x**2 + y**2 + z**2)


def smoother(a: point, b: point, c: point, d: float):
    angle = acos(())


# def lower()


class planer(object):
    def __init__(self) -> None:
        self.timestep = 1 / 1000  # s
        self.maxspeed = 2  # m/s
        self.maxacc = 10  # m/s²
        self.jerk = 100  # m/s³
        self.postarget = 1 / 100000  # m
        self.speedtarget = 1 / 100  # m/s
        self.acctarget = 1 / 10  # m/s²
        pass

    def integrate(self, times: list[float], vin: float = 0):
        """Integrates time list to get path end parameters.

        Args:
            times (list): list of 7 time intervals to integrate
            vin (float, optional): Speed at start point. Defaults to 0.

        Returns:
            pos, speed, acc (float): integration results at endpont (or when times list will end)
        """
        jerks = [1, 0, -1, 0, -1, 0, 1]
        pos = 0
        speed = vin
        acc = 0
        for j, t in zip(jerks, times):
            # Will stop iterrate on last t if t is not full length! Useful for iterratin on a part of path!
            j = self.jerk * j
            nacc = j * t + acc
            nspeed = j * (t**2) / 2 + acc * t + speed
            pos = j * (t**3) / 3 + acc * (t**2) / 2 + speed * t + pos
            acc = nacc
            speed = nspeed
        return pos, speed, acc

    def calcerrors(
        self, t: list[float], length: float, vin: float, vout: float
    ) -> list[float]:
        """Integrates time intervals and calculates solution errors, also returns total trip time and rms error

        Args:
            t (list[float]): List containing time intervals
            length (float): Trip target length, m
            vin (float): Speed at start point, m/s
            vout (float): Speed at end point, m/s

        Returns:
            list[float]:
                0: Position error, m
                1: Speed error, m/s
                2: Total treep time, s
                3: RMS error + treep time (it is supposed that as this par goes lower than the solution is better)
        """
        pos, speed, acc = self.integrate(t, vin)
        epos = length - pos
        espeed = vout - speed
        sumt = sum(t)
        rms = sqrt(10 * epos**2 + 10 * espeed**2 + sumt**2)
        return epos, espeed, sumt, rms

    def intbystep(
        self, times: list[float], timestep: float = 1 / 1000, vin: float = 0
    ) -> list:
        """Integrates timelist step by step. And generates lists containing results.

        Args:
            times (list[float]): time interval lists
            timestep (float, optional): Integration step in seconds. Defaults to 1/1000.
            vin (float, optional): Speed at start point in m/s. Defaults to 0.

        Returns:
            list of lists (floats): lists containing:
                0: time
                1: position
                2: speed
                3: acceleration
                4: jerk
        """
        results = [[], [], [], [], []]
        pos = 0
        speed = vin
        acc = 0
        time = 0
        jerks = [1, 0, -1, 0, -1, 0, 1]
        timeends = [0]
        for t in times:
            timeends.append(timeends[-1] + t)
        timeends.pop(0)
        step = 0
        while time < timeends[-1]:
            if time >= timeends[step]:
                step += 1

            jerk = self.jerk * jerks[step]
            results[4].append(jerk)
            acc += jerk * timestep
            results[3].append(acc)
            speed += acc * timestep
            results[2].append(speed)
            pos += speed * timestep
            results[1].append(pos)
            time += timestep
            results[0].append(time)

        return results

    def plan(
        self,
        length: float,
        vin: float = 0,
        vout: float = 0,
        plotter: callable = None,
        resetonoscil=False,
    ):
        """Calculates movement plan - a list of 7 time intervals, describing the movement.

        Args:
            length (float): Distance to move, m
            vin (float, optional): Speed at start point, m/s. Defaults to 0.
            vout (float, optional): Speed at end point, m/s. Defaults to 0.
            plotter (callable, optional): Function to call on every loop. Defaults to None. Usefull for debuging. Parameters are:
                t: current time list
                i: Solution step
                epos: current position error
                espeed: current speed error
                sumt: total treep time (calculated)
                rms: RMS error+time (see planer.calcerrors)
                ptime: time from solving started
            resetonoscil (bool, optional): If True solution will be rastarted on oscillation. Usefull for very small distances. Defaults to False.

        Returns:
            t (list[Float]): List of 7 time intervals, describing the movement
            i (int): number of iterations needed to find solution
            time (float): Time needed to find solution, s
        """
        t = [0, 0, 0, 0, 0, 0, 0]
        i = 0
        epos = length
        espeed = vout - vin
        starttime = time()
        prevepossign = 1
        osccounter = 0
        while abs(epos) > self.postarget or abs(espeed) > self.speedtarget:

            i += 1  # Current solution step number

            epos, espeed, sumt, rms = self.calcerrors(t, length, vin, vout)
            if plotter:
                ptime = time() - starttime
                plotter(t, i, epos, espeed, sumt, rms, ptime)

            # Oscilation detection
            epossign = copysign(1, epos)
            # print(epossign)
            if epossign != prevepossign:
                osccounter += 1
                prevepossign = epossign
            if osccounter > 100:
                self.timestep = self.timestep / 2
                print(f"Oscilation! Reduced timestep to: {self.timestep}")
                # sleep(2)
                osccounter = 0
                if resetonoscil:
                    t = [0, 0, 0, 0, 0, 0, 0]
                    print("Restarting")

            if epos > self.postarget:
                # Rise jerk time
                if (
                    t[0] < self.maxacc / self.jerk
                    and self.integrate(t[0:3], vin)[1] < self.maxspeed
                ):
                    t[0] += self.timestep
                    t[2] = t[0]
                elif self.integrate(t[0:3], vin)[1] < self.maxspeed:
                    t[1] += self.timestep
                else:
                    t[3] += self.timestep
                # Rise acc time

                # Rise travel time

            elif epos < -self.postarget:
                # Lower travel time
                if t[3] > 0:
                    t[3] = max(t[3] - self.timestep, 0)
                # Lower acc time
                elif t[1] > 0:
                    t[1] = max(t[1] - self.timestep, 0)
                # Lower jerk time
                else:
                    t[0] = max(t[0] - self.timestep, 0)
                    t[2] = t[0]

            # Lets integrate timelist and calculate errors again to correct vout error
            epos, espeed, sumt, rms = self.calcerrors(t, length, vin, vout)
            if espeed < -self.speedtarget:
                # Rise neg jerk time
                if t[4] < self.maxacc / self.jerk:
                    t[4] += self.timestep
                    t[6] = t[4]
                # Rise neg acc time
                else:
                    t[5] += self.timestep

            elif espeed > self.speedtarget:
                # Lower neg acc time
                if t[5] > 0:
                    t[5] = max(t[5] - self.timestep, 0)
                else:
                    t[4] = max(t[4] - self.timestep, 0)
                    t[6] = t[4]
                # Lower neg jerk time

        return t, i, time() - starttime
