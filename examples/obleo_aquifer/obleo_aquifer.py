import os
import numpy as np
import matplotlib.pyplot as plt
import flopy.modflow as mf
import flopy.utils as fu
import shutil

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

name = 'obleo_aquifer'

# --- Setting up the parameters
# Groundwater heads
hLakes = 0  # in the boundaries

# Number of layers
NLay = 1

# Number of columns and rows
# we are assuming that NCol = NRow
# and we add on the left and right side one more column
# which are representing the lakes
NRow = 11
NCol = 1 + 11 + 1

# The length and with of the model in meters
# To the width of the model area we add on the left and right
# side one more column which are representing the lakes
Height = 11e+5
Width = 1e+5 + 11e+5 + 1e+5

# The height of the model
H = 1000
hy = 36500
sf1 = 0.25

# Instantiate the ModFlow-Object, ml is here an invented name
ml = mf.Modflow(modelname=name, exe_name='mf2005', version='mf2005', model_ws=workspace)

# The aquifer is about 1000m thick with top elevation of 100m
top = 100

# The aquifer is about 1000m thick, so the bottom is estimated to be on -900m
bot = -900

# Calculation of row-width and col-width
delr = Height / NRow
delc = Width / NCol

# instantiate the discretization object
dis = mf.ModflowDis(ml, nlay=NLay, nrow=NRow, ncol=NCol, delr=delr, delc=delc, top=top, botm=bot, laycbd=0, itmuni=5, perlen=30, nper=2)

# every cell in the model has to be defined
# create an 3-dimensional iBound-array with all cells=1
iBound = np.ones((NLay, NRow, NCol))

# Set every first element of every column to -1
iBound[:, :, 0] = -1

# Set every last element of every column to -1
iBound[:, :, -1] = -1

# defining the start-values
# in the calculation only the -1 cells will be considered
# because of this, all values can be set to hLakes
start = 0 * np.ones((NRow, NCol))

# instantiate the modFlow-basic package with iBound and startValues
bas = mf.ModflowBas(ml, ibound=iBound, strt=start)

# setting up recharge data and recharge package
recharge_data = 250.e-3
rch = mf.ModflowRch(ml, nrchop=1, rech=recharge_data)

# setting up the well package with stress periods
stress_period_data = {
    0: [[0, NRow / 2, NCol / 2, 0.]],
    1:  [[0, NRow / 2, NCol / 2, -4.31e+10]]
}

wel = mf.ModflowWel(ml, stress_period_data=stress_period_data)

# set the aquifer properties with the lpf-package
bcf = mf.ModflowBcf(ml, hy=hy, sf1=sf1, laycon=1)
 
# instantiation of the solver with default values
pcg = mf.ModflowPcg(ml)

# instantiation of the output control with default values
oc = mf.ModflowOc(ml)

ml.write_input()
ml.run_model()

hds = fu.HeadFile(os.path.join(workspace, name+'.hds'))

h = hds.get_data(kstpkper=(0, 0))
x = np.linspace(0, Width, NCol)
y = np.linspace(0, Height, NRow)
c = plt.contour(x, y, h[0], np.arange(500, 1000, 50))
plt.clabel(c, fmt='%2.1f')
plt.axis('scaled')
plt.axis((0, Width, 0, Height))
plt.savefig(os.path.join(output, name+'_SP1.png'))
plt.close()

h = hds.get_data(kstpkper=(0, 1))
x = np.linspace(0, Width, NCol)
y = np.linspace(0, Height, NRow)
c = plt.contour(x, y, h[0], np.arange(500, 1000, 50))
plt.clabel(c, fmt='%2.1f')
plt.axis('scaled')
plt.axis((0, Width, 0, Height))
plt.savefig(os.path.join(output, name+'_SP2.png'))
plt.close()
