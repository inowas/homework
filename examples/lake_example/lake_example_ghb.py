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

name = 'lake_example_ghb'

# --- Setting up the parameters
# Groundwater heads
h1 = 100  # in the boundaries
h2 = 90   # water-level-lake

# Number of layers
Nlay = 10

# Number of columns and rows
# we are assuming that NCol = NRow
N = 11

# The length and with of the model
L = 400.0 

# The height of the model
H = 50.0 
k = 1.0

#  Instantiate the ModFlow-Object, ml is here an invented name
ml = mf.Modflow(modelname=name, exe_name='mf2005', version='mf2005', model_ws=workspace)

# Calculation of the bottom-height of each layer
# more information: http://docs.scipy.org/doc/numpy-1.10.0/reference/generated/numpy.linspace.html
bot = np.linspace(-H/Nlay, -H, Nlay)
# result is: 
# array([ -5., -10., -15., -20., -25., -30., -35., -40., -45., -50.])


# calculation of row-width and col-width
delrow = delcol = L/(N-1) 
# result is: 
# 4

# instantiante the discretization object
dis = mf.ModflowDis(ml, nlay=Nlay, nrow=N, ncol=N, delr=delrow, delc=delcol, nper=7, top=0.0, botm=bot, laycbd=0)

# helping-variable
Nhalf = (N-1)/2 

# iBound-Configuration
# http://water.usgs.gov/nrp/gwsoftware/modflow2000/MFDOC/index.html?bas6.htm
# If IBOUND(J,I,K) < 0, cell J,I,K has a constant head.
# If IBOUND(J,I,K) = 0, cell J,I,K is inactive.
# If IBOUND(J,I,K) > 0, cell J,I,K is active.
#
# every cell in the model has to be defined
# create an 3-dimensional ibound-array with all cells=1
ibound = np.ones((Nlay, N, N))
# result is:
# array([[[ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         ..., 
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.]],
# 
#        [[ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         ..., 
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.]],
# 
#        [[ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         ..., 
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.]],
# 
#        ..., 
#        [[ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         ..., 
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.]],
# 
#        [[ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         ..., 
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.]],
# 
#        [[ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         ..., 
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.],
#         [ 1.,  1.,  1., ...,  1.,  1.,  1.]]])

# Set every first element of every column to -1
ibound[:, :, 0] = -1

#  result is:
#  array([[[-1., -1., -1., ..., -1., -1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        ..., 
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1., -1., -1., ..., -1., -1., -1.]],
#
#       [[-1., -1., -1., ..., -1., -1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        ..., 
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1., -1., -1., ..., -1., -1., -1.]],
#
#       [[-1., -1., -1., ..., -1., -1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        ..., 
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1., -1., -1., ..., -1., -1., -1.]],
#
#       ..., 
#       [[-1., -1., -1., ..., -1., -1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        ..., 
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1., -1., -1., ..., -1., -1., -1.]],
#
#       [[-1., -1., -1., ..., -1., -1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        ..., 
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1., -1., -1., ..., -1., -1., -1.]],
#
#       [[-1., -1., -1., ..., -1., -1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        ..., 
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1.,  1.,  1., ...,  1.,  1., -1.],
#        [-1., -1., -1., ..., -1., -1., -1.]]])

# set center cell in upper layer to constant head (-1)
ibound[0, Nhalf, Nhalf] = -1
ibound[0, 0, 0] = 1

# defining the start-values
# in the calculation only the -1 cells will be considered
#
# all values are set to h1
start = h1 * np.ones((N, N))
# and the center value is set to h2
start[Nhalf, Nhalf] = h2

# instantiate the modflow-basic package with iBound and startvalues
bas = mf.ModflowBas(ml, ibound=ibound, strt=start)

# set the aquifer properties with the lpf-package
lpf = mf.ModflowLpf(ml, hk=k)

# set Time-Variant Specified-Head Package chd
# ghb_dtype = mf.ModflowGhb.get_default_dtype()
stress_period_data = \
    {
        0: [
            [0, 0, 10, 80., 100.],
            [0, 1, 10, 80., 100.],
            [0, 2, 10, 80., 100.],
            [0, 3, 10, 80., 100.],
            [0, 4, 10, 80., 100.],
            [0, 5, 10, 80., 100.],
            [0, 6, 10, 80., 100.],
            [0, 7, 10, 80., 100.],
            [0, 8, 10, 80., 100.],
            [0, 9, 10, 80., 100.],
            [0, 10, 10, 80., 100.]
        ]
    }
ghb = mf.ModflowGhb(ml, stress_period_data=stress_period_data)
 
# instantiation of the solver with default values
pcg = mf.ModflowPcg(ml)

# instantiation of the output control with default values
oc = mf.ModflowOc(ml)

ml.write_input()
ml.run_model()

hds = fu.HeadFile(os.path.join(workspace, name+'.hds'))
h = hds.get_data(kstpkper=(0, 1))

x = y = np.linspace(0, L, N)
c = plt.contour(x, y, h[0], np.arange(90, 100.1, 0.5))
plt.clabel(c, fmt='%2.1f')
plt.axis('scaled')
plt.savefig(os.path.join(output, name+'_1.png'))
plt.close()

x = y = np.linspace(0, L, N)
c = plt.contour(x, y, h[-1], np.arange(90, 100.1, 0.5))
plt.clabel(c, fmt='%1.1f')
plt.axis('scaled')
plt.savefig(os.path.join(output, name+'_2.png'))
plt.close()
