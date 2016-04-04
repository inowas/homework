import os
import numpy as np
import matplotlib.pyplot as plt
import flopy.modflow as mf
import flopy.utils as fu

workspace = os.path.join('data')
#make sure workspace directory exists
if not os.path.exists(workspace):
    os.makedirs(workspace)

name = 'lake_example'
h1 = 100
h2 = 90
Nlay = 10 
N = 101 
L = 400.0 
H = 50.0 
k = 1.0

ml = mf.Modflow(modelname=name, exe_name='mf2005', version='mf2005', model_ws=workspace)

bot = np.linspace(-H/Nlay,-H,Nlay) 
delrow = delcol = L/(N-1) 
dis = mf.ModflowDis(ml,nlay=Nlay,nrow=N,ncol=N,delr=delrow,delc=delcol,top=0.0,botm=bot,laycbd=0) 

Nhalf = (N-1)/2 
ibound = np.ones((Nlay,N,N)) 
ibound[:,0,:] = -1; ibound[:,-1,:] = -1; ibound[:,:,0] = -1; ibound[:,:,-1] = -1 
ibound[0,Nhalf,Nhalf] = -1 
start = h1 * np.ones((N,N)) 
start[Nhalf,Nhalf] = h2 
bas = mf.ModflowBas(ml,ibound=ibound,strt=start)
lpf = mf.ModflowLpf(ml, hk=k)
pcg = mf.ModflowPcg(ml)
oc = mf.ModflowOc(ml) 

ml.write_input()
ml.run_model()

hds = fu.HeadFile(os.path.join(workspace, name+'.hds'))
h = hds.get_data(kstpkper=(0, 0))

x = y = np.linspace(0, L, N)
c = plt.contour(x, y, h[0], np.arange(90,100.1,0.2))
plt.clabel(c, fmt='%2.1f')
plt.axis('scaled');
plt.savefig(os.path.join(workspace, name+'_1.png'))
plt.close()

x = y = np.linspace(0, L, N)
c = plt.contour(x, y, h[-1], np.arange(90,100.1,0.2))
plt.clabel(c, fmt='%1.1f')
plt.axis('scaled');
plt.savefig(os.path.join(workspace, name+'_2.png'))
plt.close()

z = np.linspace(-H/Nlay/2, -H+H/Nlay/2, Nlay)
c = plt.contour(x, z, h[:,50,:], np.arange(90,100.1,.2))
plt.axis('scaled');
plt.savefig(os.path.join(workspace, name+'_3.png'))
plt.close()





