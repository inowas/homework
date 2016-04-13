# -*- coding: utf-8 -*-
"""
@author: aybulat
"""
import flopy
import numpy as np
import os


################################# CONTROL SECTION

################################# INPUT USING COMMAND LINE ARGUMENTS
# If uncomment this section, control parameters can be defined with script execution as command line arguments
# for exapmle: 'python test.py 10 10 100 0.002 50 -1000 1 1'
import sys
nx = int(sys.argv[1])
ny= int(sys.argv[2])
nper = int(sys.argv[3])
rch = float(sys.argv[4])
avgHead = float(sys.argv[5])
avgRate = float(sys.argv[6])
amplitudeHead = float(sys.argv[7])
amplitudeRate = float(sys.argv[8])

################################# RUN WITH PREDEFINED PARAMETERS
# If uncomment this section, predefined control parameters will be used
# and programm should be executed as for exapmle: 'python test.py'
#nx = 10 #model resulution
#ny = 10
#nper = 100 #number of stress periods
#rch = 0.002 #constant dayly recharge value in meters
#avgHead = 50 # average boundary head value used in computing CHD sinusoidal stress period data and initial head coverage
#avgRate = - 1000 # average well pumping rate used in computing WEL sinusoidal stress period data
#amplitudeHead = 1 # amplitude of boundary head variations used in computing CHD sinusoidal stress period data
#amplitudeRate = 1 # amplitude of well pumping rate variations used in computing WEL sinusoidal stress period data


################################# CALCULATION SECTION #####
nstp = 1 # number of steps equal to number of periods
perlen = list(np.ones(nper)) # list of stress periods lenghts
nlay = 1 # one layer
xmin = 0. # model area extensions, m 
xmax = 1000.
ymin = 0.
ymax = 1000.
delc = (xmax - xmin)/nx # grid cell size
delr = (ymax - ymin)/ny
wellLocation = [500,500] # location of the pumping well
wellC = (nx - 1) - int((xmax - wellLocation[0])/delc) # transformation of the x/y corinates to row/column
wellR = (ny - 1) - int((ymax - wellLocation[1])/delr) # transformation of the corinates to row/column

grid = np.ones((nx, ny))
#ibound = np.ones((nlay, nx, ny))# model grid, 1 is for active model cell
top = grid * 100 # top elevation grid
bottom = grid * 0 # bottom elevetion grid
strt = grid * avgHead # initial head grid
hk = grid * 1 # hydraulic conductivity grid
stress_period_list = range(nstp) # list of stress periods used in stress period data constructing
# lists rows and columns describing location of the head boundary
boundaryCols, boundaryRows = [],[] 
# filling lists of rows and columns, making boundary always to be at the perimeter of rectangular area
boundaryCols += [0 for i in range(ny)]
boundaryCols += [nx-1 for i in range(ny)]
boundaryCols += [i for i in range(nx) if i != 0 and i != nx-1]
boundaryCols += [i for i in range(nx) if i != 0 and i != nx-1]

boundaryRows += [i for i in range(ny)]
boundaryRows += [i for i in range(ny)]
boundaryRows += [0 for i in range(nx) if i != 0 and i != nx-1]
boundaryRows += [ny-1 for i in range(nx) if i != 0 and i != nx-1]

# adding variability to boundary head and well pumping rate, making sinusoidal time-series
sin = np.sin(np.array(range(nper)) * np.pi / (nper/2.)) # sin array, simulation period is a single cycle with sin starting end ending at 0
boundVals = sin * amplitudeHead + avgHead # constructing timeseries envolving sin, amplitude and average values
wellVals = sin * amplitudeRate + avgRate

spdWell = {} # building well stress period data dictionary
for period in stress_period_list:
    spdWell[period] = [0, wellR, wellC, wellVals[period]]
    
spdBound = {} # building boundary stress period data dictionary
for period in stress_period_list:
    SPD_single = []
    for i in range(len(boundaryCols)):
        SPD_single.append([0, boundaryRows[i], boundaryCols[i], boundVals[period], boundVals[period]])
        spdBound[period] = SPD_single


################################# Creating model files and execution the model
name = 'base_performance_test'
workspace = os.path.join('data')
if not os.path.exists(workspace):
    os.makedirs(workspace)

MF = flopy.modflow.Modflow(name, exe_name='mf2005', version='mf2005', model_ws=workspace)
DIS_PACKAGE = flopy.modflow.ModflowDis(MF, nlay, ny, nx, delr=delr,botm=bottom, delc=delc,top=top, laycbd=0, steady=False, nper = nper, nstp = nstp, perlen = perlen)
BAS_PACKAGE = flopy.modflow.ModflowBas(MF, ibound=grid, strt=strt, hnoflo = -9999)
OC_PACKAGE = flopy.modflow.ModflowOc(MF)
RCH_PACKAGE = flopy.modflow.ModflowRch(MF, rech=rch)
LPF_PACKAGE = flopy.modflow.ModflowLpf(MF, hk=hk, laytyp = 1)
PCG_PACKAGE = flopy.modflow.ModflowPcg(MF, mxiter=900, iter1=900)
CHD = flopy.modflow.ModflowChd(MF, stress_period_data = spdBound)
WEL = flopy.modflow.ModflowWel(MF, stress_period_data = spdWell)
MF.write_input()
MF.run_model()
################################ Reading Modflow output
headfileobj = flopy.utils.HeadFile(os.path.join(workspace, name+'.hds'))
HEAD = headfileobj.get_data(totim = 1)
heads_list = HEAD[0].tolist()
