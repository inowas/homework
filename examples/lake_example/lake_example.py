import os
import numpy as np
import matplotlib.pyplot as plt


import flopy.modflow as mf
import flopy.utils as fu
import pprint
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

name = 'lake_example'

# --- Setting up the parameters
# Groundwater heads
h1 = 100 #in the boundaries
h2 = 90  # water-level-lake

# Number of layers
Nlay = 10

# Number of columns and rows
# we are assuming that NCol = NRow
N = 101 

# The length and with of the model
L = 400.0 

# The height of the model
H = 50.0 
k = 1.0

# Intstantiating the Modflow-Object, ml is here an invented name
ml = mf.Modflow(modelname=name, exe_name='mf2005', version='mf2005', model_ws=workspace)

# Calculation of the bottom-height of each layer
# more information: http://docs.scipy.org/doc/numpy-1.10.0/reference/generated/numpy.linspace.html
bot = np.linspace(-H/Nlay,-H,Nlay) 
# result is: 
# array([ -5., -10., -15., -20., -25., -30., -35., -40., -45., -50.])


# calculation of row-width and col-width
delrow = delcol = L/(N-1) 
# result is: 
# 4

# instantiante the discretization object
dis = mf.ModflowDis(ml, nlay=Nlay, nrow=N, ncol=N, delr=delrow, delc=delcol, top=0.0, botm=bot, laycbd=0)

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
ibound = np.ones((Nlay,N,N)) 
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


# Set all elements in the first row to -1
ibound[:,0,:] = -1 

# Set all elements in the last row to -1
ibound[:,-1,:] = -1

# Set every first element of every column to -1
ibound[:,:,0] = -1

# Set every last element of every column to -1
ibound[:,:,-1] = -1

#result is:
#array([[[-1., -1., -1., ..., -1., -1., -1.],
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
Nhalf=int(Nhalf)
ibound[0,Nhalf,Nhalf] = -1 

# defining the start-values
# in the calculation only the -1 cells will be considered
#
# all values are set to h1
start = h1 * np.ones((N,N))
# and the center value is set to h2
start[Nhalf,Nhalf] = h2

# instantiate the modflow-basic package with iBound and startvalues
bas = mf.ModflowBas(ml,ibound=ibound,strt=start)

# set the aquifer properties with the lpf-package
lpf = mf.ModflowLpf(ml, hk=k)
 
# instantiation of the solver with default values
pcg = mf.ModflowPcg(ml)

# instantiation of the output control with default values
oc = mf.ModflowOc(ml)

ml.write_input()
ml.run_model()

hds = fu.HeadFile(os.path.join(workspace, name+'.hds'))
h = hds.get_data(kstpkper=(0, 0))

x = y = np.linspace(0, L, N)
c = plt.contour(x, y, h[0], np.arange(90,100.1,0.2))
plt.clabel(c, fmt='%2.1f')
plt.axis('scaled');
plt.savefig(os.path.join(output, name+'_1.png'))
plt.close()

x = y = np.linspace(0, L, N)
c = plt.contour(x, y, h[-1], np.arange(90,100.1,0.2))
plt.clabel(c, fmt='%1.1f')
plt.axis('scaled');
plt.savefig(os.path.join(output, name+'_2.png'))
plt.close()

z = np.linspace(-H/Nlay/2, -H+H/Nlay/2, Nlay)
c = plt.contour(x, z, h[:,50,:], np.arange(90,100.1,.2))
plt.axis('scaled');
plt.savefig(os.path.join(output, name+'_3.png'))
plt.close()