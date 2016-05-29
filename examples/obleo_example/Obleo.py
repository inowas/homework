'Obleo example'

import os
import numpy as np
import matplotlib.pyplot as plt
import flopy.modflow as mf
import flopy.utils as fu
import shutil
import matplotlib.colors as mc

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

workspace = os.path.join('ascii')
output = os.path.join('output')

# delete directories if existing
if os.path.exists(workspace):
    shutil.rmtree(workspace)

if os.path.exists(output):
    shutil.rmtree(output)

if not os.path.exists(workspace):
    os.makedirs(workspace)

if not os.path.exists(output):
    os.makedirs(output)

# flopy objects
modelname = 'obleo'
m = mf.Modflow(modelname=modelname, exe_name='mf2005', model_ws=workspace)

# model domain and grid definition
ztop = 100.  # top of layer (m rel to msl) !!! mls=mean sea level ???
botm = -900.  # bottom of layer (m rel to msl) !!! mls=mean sea level ???
nlay = 1  # number of layers (z)
nrow = 11  # number of rows (y)
ncol = 13  # number of columns (x)
Lx = 13e+5 # length of x model domain, in m
Ly = 11e+5 # length of y model domain, in m
delr = Lx / ncol  # row width of cell, in m
delc = Ly / nrow  # column width of cell, in m


# define the stress periods
nper = 2
ts = 1  # length of time step, in years
nstp = 30  # number of time steps
perlen = nstp * ts  # length of simulation, in years
steady = True  # steady state or transient

dis = mf.ModflowDis(m, nlay, nrow, ncol, delr=delr, delc=delc, top=ztop, botm=botm, nper=nper, perlen=perlen, nstp=nstp, steady=steady, itmuni=5)


# hydraulic parameters (aquifer properties with the bcf-package)
hy = 36500 # hydraulic conductivity
sf = 0.25 # storage coefficient
laycon = 1 # layer type, confined (0), unconfined (1), constant T, variable S (2), variable T, variable S (default is 3)
bcf = mf.ModflowBcf(m, hy=hy, sf1=sf, laycon=1)

# BAS package (Basic Package)
ibound = np.ones((nlay, nrow, ncol)) # # active cells
ibound[:, :, 0] = -1 # Set every first element of every column to -1
ibound[:, :, -1] = -1 # Set every last element of every column to -1
strt = 0 * np.ones((nrow, ncol)) # in the calculation only the -1 cells will be considered (all values can be set to 0)
bas = mf.ModflowBas(m, ibound=ibound, strt=strt)


# setting up recharge data and recharge package
recharge_data = 0.250 # recharge flux mm/year (default is 1.e-3)
nrchop = 1 # optional code (1: to top grid layer only; 2: to layer defined in irch 3: to highest active cell)
rch = mf.ModflowRch(m, nrchop=nrchop, rech=recharge_data)

# setting up the well package with stress periods
pumping_rate = -4e+10 # m^3 / year
lrcq = {0: [[0, 5, 6, 0.]], 1: [[0, 5, 6, -4e+10]]} 
wel = mf.ModflowWel(m, stress_period_data=lrcq)

# instantiation of the solver with default values
pcg = mf.ModflowPcg(m) # pre-conjugate gradient solver

# instantiation of the output control with default values
oc = mf.ModflowOc(m) # output control

m.write_input()
m.run_model()

hds = fu.HeadFile(os.path.join(workspace, modelname+'.hds'))
h = hds.get_data(kstpkper=(0, 0))

x = np.linspace(0, Lx, ncol)
y = np.linspace(0, Ly, nrow)
c = plt.contour(x, y, h[0], np.arange(500, 1000, 50))
plt.clabel(c, fmt='%2.1f')
plt.axis('scaled')
plt.axis((0, Lx, 0, Ly))
plt.savefig(os.path.join(output, modelname+'_SP1.png'))
plt.show()

h = hds.get_data(kstpkper=(0, 1))
x = np.linspace(0, Lx, ncol)
y = np.linspace(0, Ly, nrow)
c = plt.contour(x, y, h[0], np.arange(500, 1000, 50))
plt.clabel(c, fmt='%2.1f')
plt.axis('scaled')
plt.axis((0, Lx, 0, Ly))
plt.savefig(os.path.join(output, modelname+'_SP2.png'))
plt.show()

# Output based on this example: http://matplotlib.org/mpl_toolkits/mplot3d/tutorial.html#surface-plots
fig = plt.figure()
ax = fig.gca(projection='3d')
X = np.linspace(0, Lx, ncol)
Y = np.linspace(0, Ly, nrow)
X, Y = np.meshgrid(X, Y)
Z = h[0]  # set layer 1

norm = mc.Normalize(vmin=0, vmax=np.max(Z), clip=False)  # set min/max of the colors
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.Set1, linewidth=-0.005, antialiased=False, norm=norm)
ax.set_zlim(0, 1000)  # set limit of z-axis
ax.xaxis.set_major_locator(LinearLocator(2))
ax.yaxis.set_major_locator(LinearLocator(2))
ax.zaxis.set_major_locator(LinearLocator(2))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.01f'))
fig.colorbar(surf, shrink=0.7, aspect=10)
plt.savefig(os.path.join(output, modelname+'_SP3.png'))
ax.set_xlabel('meters')
ax.set_zlabel('meters')
plt.show()

m.check()