from profiler import planer
import matplotlib.pyplot as plt
from time import sleep

# y = []


def plotter(t, i, epos, espeed, sumt, rms, ptime):
    # print(i, epos)
    # y.append(epos)
    # x.append(i)
    # line.set_data(x, y)
    # plt.draw()
    # plt.pause(0.01)
    # print(t)
    # sleep(0.01)
    # print(f"epos: {epos}, espeed:{espeed}")
    # print(t)
    pass


pln = planer()
pln.maxspeed = 1
pln.timestep = 1 / 1000
pln.speedtarget= 1/1000
pln.jerk =500
pln.postarget = 1 / 100000
# length, speed, acc = pln.integrate([ 0.01, 0.2, 0.01, 0.5, 0.01, , 1])
t, i, runtime = pln.plan(1,resetonoscil=False)
print(t, i, runtime, sum(t))
intres = pln.intbystep(t, 1 / 100000)

fig, ax = plt.subplots(3, sharex=True)
ax[0].plot(intres[0], intres[1])
ax[1].plot(intres[0], intres[2])
ax[2].plot(intres[0], intres[3])
plt.show()
