import os

import matplotlib.pyplot as plt
import flopy.modflow as mf
import flopy.utils.formattedfile as ff
import pprint

workspace = os.path.join('data')
pprint.pprint(workspace)

modelname = 'Model_for_Pirna'
ml = mf.Modflow.load(modelname+'.nam', exe_name='mf2005', model_ws=workspace, verbose=True)

#  pprint.pprint(ml.dis)
#pprint.pprint(ml.dis.top.array)
#ml.write_input()
ml.run_model()

hdobj = ff.FormattedHeadFile(os.path.join(workspace, modelname+'.fhd'), precision='single')
kstpkper = hdobj.get_kstpkper()

times = hdobj.get_times()

days = []
resultsG21L2 = []
for x in range(0, len(kstpkper)):
    data = hdobj.get_data(idx=x)
    days.append((times[x]/86400)+4901)
    resultsG21L2.append(data[1][10][69])

#  plt.plot_date(days, resultsG21L2)
#  plt.ylabel('heads')
#  plt.legend(['Layer 2'], loc='upper right')
#  plt.show()
