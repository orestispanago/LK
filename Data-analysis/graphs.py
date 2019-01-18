import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import glob
import os


class Sim:
    cases = []

    def __init__(self, df, sunpos):
        """
        :param pandas.core.frame.DataFrame df: raytrace data for sun position
        :param str sunpos: sun position (x in SolTrace)
        """
        self.df = df
        self.sunpos = sunpos
        Sim.cases.append(self)


def update_hist(num):
    z = Sim.cases[num].df['z']
    plt.cla()
    plt.hist(z, bins=50)
    ax.set_ylim(0, 5000)
    ax.set_xlabel('z')
    ax.set_ylabel('Count')
    plt.title('Sun position: ' + Sim.cases[num].sunpos)


def update_scatter(num):
    x = Sim.cases[num].df['y']
    y = Sim.cases[num].df['z']
    plt.cla()
    plt.scatter(x.values, y.values, s=2)
    ax.set_ylim(0, 0.28)
    ax.set_xlabel(x.name)
    ax.set_ylabel(y.name)
    plt.title('Sun position: ' + Sim.cases[num].sunpos)


cwd = os.getcwd()
outdir = cwd + '/output/'
if not os.path.exists(outdir):
    os.makedirs(outdir)

csvfiles = glob.glob(cwd + '/raw/*.csv')
csvfiles.sort(key=lambda x: int(os.path.split(x)[1][:-4]))

for f in csvfiles:
    sun_pos = os.path.split(f)[1][:-4]
    dfr = pd.read_csv(f)
    dfr = dfr[dfr['element'] == -4]  # select hits on absorber
    Sim(dfr, sun_pos)
fig, ax = plt.subplots()

animation = FuncAnimation(fig, update_scatter, len(Sim.cases),
                          interval=500)
plt.show()


# animation.save(outdir+'histogram_0_1000_step50.gif', dpi=80, writer='pillow')
