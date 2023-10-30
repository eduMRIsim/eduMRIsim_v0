import sys
import numpy as np
from scipy.io import loadmat

data = loadmat("models/Generated.mat").get("mat")

PDmap = data[:,:,:,0]
T1map = data[:,:,:,1]
T2map = data[:,:,:,2]

np.save("models/model1/PDmap", PDmap)
np.save("models/model1/T1map", T1map)
np.save("models/model1/T2map", T2map)