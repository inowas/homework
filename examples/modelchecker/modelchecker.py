import os
import flopy

path = os.path.join('data', 'mf2005_test')

m = flopy.modflow.Modflow.load('test1ss.nam', model_ws=path)
m.change_model_ws('data')

m.rch.check()