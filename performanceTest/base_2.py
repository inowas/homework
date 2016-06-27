"""
 This script is part of a study-project by TU-Dresden
  We try to investigate model-complexity with calculation time
  Base script 'Obleo'

"""
import os
import numpy as np
import flopy.modflow as mf
import shutil
import sys
from datetime import datetime

workspace = os.path.join('ascii')


# delete directories if existing
if os.path.exists(workspace):
    shutil.rmtree(workspace)

if not os.path.exists(workspace):
    os.makedirs(workspace)

# flopy objects
modelname = 'performance_test'
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

timeStartWritingInput = datetime.now()
ml.write_input()
timeStartRunningModel = datetime.now()
ml.run_model()
timeEndRunningModel = datetime.now()
print "Time writing input: "+str(timeStartRunningModel-timeStartWritingInput)
print "Calculation Time: "+str(timeEndRunningModel-timeStartRunningModel)

if os.path.exists(workspace):
    shutil.rmtree(workspace)