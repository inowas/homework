"""
 This script is part of a study-project by TU-Dresden
 We try to investigate model-complexity with calculation time
 This script compares different river conductance value, where one argument will be needed 

"""
import os
import numpy as np
import flopy.modflow as mf
import shutil
import sys

workspace = os.path.join('ascii')

# delete directories if existing
if os.path.exists(workspace):
    shutil.rmtree(workspace)

if not os.path.exists(workspace):
    os.makedirs(workspace)

name = 'performance_test'

# --- Setting up the parameters
# Groundwater heads
h1 = 100  # in the boundaries
h2 = 90   # water-level-lake

# Number of layers
NLay = 10

# Number of columns and rows
# we are assuming that NCol = NRow
N = 101

# The length and with of the model
L = 400.0 

# The height of the model
H = 50.0 
k = 1.0

# Instantiating the ModFlow-Object, ml is here an invented name
ml = mf.Modflow(modelname=name, exe_name='mf2005', version='mf2005', model_ws=workspace)

# Calculation of the bottom-height of each layer
bot = np.linspace(-H / NLay, -H, NLay)

# Calculation of row-width and col-width
delRow = delCol = L/(N-1)

# Number of timePeriods
nPer = 100

# Set steady of all periods to false
steady = np.zeros(100)

# Instantiate the discretization object
dis = mf.ModflowDis(ml, nlay=NLay, nrow=N, ncol=N, delr=delRow, delc=delCol, top=0.0, botm=bot, laycbd=0, lenuni=2, itmuni=4, steady=steady, nper=nPer, perlen=1)

# helping-variable
NHalf = int((N-1)/2)

# iBound-Configuration
iBound = np.ones((NLay, N, N))

# Set all elements in the first row to -1
iBound[:, 0, :] = -1

# Set all elements in the last row to -1
iBound[:, -1, :] = -1

# Set every first element of every column to -1
iBound[:, :, 0] = -1

# Set every last element of every column to -1
iBound[:, :, -1] = -1


# set center cell in upper layer to constant head (-1)
iBound[0, NHalf, NHalf] = -1

# defining the start-values
# in the calculation only the -1 cells will be considered
# all values are set to h1
start = h1 * np.ones((N, N))

# and the center value is set to h2
start[NHalf, NHalf] = h2

# Instantiate the ModGlow-basic package with iBound and StartValues
bas = mf.ModflowBas(ml, ibound=iBound, strt=start)

# set the aquifer properties with the lpf-package
lpf = mf.ModflowLpf(ml, hk=k)

# RIV package (setting up the riv package with stress periods)
stage = 10
riv_bot = -5.7
conductance = int(sys.argv[1])
sp =  [
		[0, 0, 1, stage, conductance, riv_bot],
		[0, 1, 1, stage, conductance, riv_bot],
		[0, 2, 1, stage, conductance, riv_bot],
		[0, 3, 1, stage, conductance, riv_bot],
		[0, 4, 1, stage, conductance, riv_bot],
		[0, 5, 1, stage, conductance, riv_bot],
		[0, 6, 1, stage, conductance, riv_bot],
		[0, 7, 1, stage, conductance, riv_bot],
		[0, 8, 1, stage, conductance, riv_bot],
		[0, 9, 1, stage, conductance, riv_bot],
		[0, 10, 1, stage, conductance, riv_bot],
		[0, 11, 1, stage, conductance, riv_bot]
       ] 
riv = mf.ModflowRiv(ml, stress_period_data=sp)
 
# instantiation of the solver with default values
pcg = mf.ModflowPcg(ml)

# instantiation of the output control with default values
oc = mf.ModflowOc(ml)

ml.write_input()
ml.run_model()

if os.path.exists(workspace):
    shutil.rmtree(workspace)