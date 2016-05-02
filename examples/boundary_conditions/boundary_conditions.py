import os
import sys
import numpy as np
import flopy
import shutil
import pprint

workspace = os.path.join('ascii')
output = os.path.join('output')

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

name = 'boundary_conditions'

stress_period_data = [[[0, 0, 2, 10, 5000., 0],   #layer, row, column, stage, conductance, river bottom
                       [0, 1, 2, 10, 5000., 0],   #layer, row, column, stage, conductance, river bottom
                       [0, 2, 2, 10, 5000., 0]],   #layer, row, column, stage, conductance, river bottom
                     ]
m = flopy.modflow.Modflow(modelname=name, model_ws=workspace)
dis = flopy.modflow.ModflowDis(m, nper=3)
riv = flopy.modflow.ModflowRiv(m, stress_period_data=stress_period_data)

m.write_input()