import sys
import numpy as np
from scipy.io import loadmat

data = loadmat("repository/models/model1/Generated.mat").get("mat")

PDmap = data[:,:,:,0]
T1map = data[:,:,:,1]
T2map = data[:,:,:,2]

np.save("repository/models/model1/PDmap", PDmap)
np.save("repository/models/model1/T1map", T1map)
np.save("repository/models/model1/T2map", T2map)

# print minimum and maximum values of T1, T2 and PD maps
print("Minimum and maximum values of T1, T2 and PD maps")
print("T1: ", np.min(T1map), np.max(T1map))
print("T2: ", np.min(T2map), np.max(T2map))
print("PD: ", np.min(PDmap), np.max(PDmap))