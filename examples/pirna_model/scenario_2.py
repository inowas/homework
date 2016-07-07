import os

import matplotlib.pyplot as plt
import flopy.modflow as mf
import flopy.utils.formattedfile as ff
import pprint

workspace = os.path.join('scenario_2')
pprint.pprint(workspace)

modelname = 'Model_for_Pirna'

ml = mf.Modflow.load(modelname+'.nam', exe_name='mf2005', model_ws=workspace, verbose=True)
ml.run_model()

hdobj = ff.FormattedHeadFile(os.path.join(workspace, modelname+'.fhd'), precision='single')
kstpkper = hdobj.get_kstpkper()

resultsG21 = hdobj.get_ts((1, 2, 12))
for result in resultsG21:
    print "{};{}".format(result[0]/86400, result[1])

