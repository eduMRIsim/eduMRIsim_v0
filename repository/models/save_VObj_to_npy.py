import numpy as np
from scipy.io import loadmat

data = loadmat("repository/models/model2/BrainHighResolution.mat")

# Access the VObj struct
VObj_struct = data['VObj'] # <class 'numpy.ndarray'>, shape is (1,1)

# Access T1, T2, T2* and PD maps within VObj struct
T1map = VObj_struct[0,0]['T1'] # <class 'numpy.ndarray'>, shape is (216, 180, 180)
T2map = VObj_struct[0,0]['T2'] # <class 'numpy.ndarray'>, shape is (216, 180, 180)
T2smap = VObj_struct[0,0]['T2Star'] # <class 'numpy.ndarray'>, shape is (216, 180, 180)
PDmap = VObj_struct[0,0]['Rho'] # <class 'numpy.ndarray'>, shape is (216, 180, 180)

# Rotate T1map 180 degrees around the x-axis
for x_idx in range(T1map.shape[0]):
    T1map[x_idx,:,:] = np.rot90(T1map[x_idx,:,:], 2)
# Rotate T2map 180 degrees around the x-axis
for x_idx in range(T2map.shape[0]):
    T2map[x_idx,:,:] = np.rot90(T2map[x_idx,:,:], 2)
# Rotate T2smap 180 degrees around the x-axis
for x_idx in range(T2smap.shape[0]):
    T2smap[x_idx,:,:] = np.rot90(T2smap[x_idx,:,:], 2)
# Rotate PDmap 180 degrees around the x-axis
for x_idx in range(PDmap.shape[0]):
    PDmap[x_idx,:,:] = np.rot90(PDmap[x_idx,:,:], 2) 

# Display T1 map
import matplotlib.pyplot as plt
plt.imshow(PDmap[:,:,40], cmap='gray')
plt.show()

np.save("repository/models/model2/T1map", T1map)
np.save("repository/models/model2/T2map", T2map)
np.save("repository/models/model2/T2smap", T2smap)
np.save("repository/models/model2/PDmap", PDmap)

TE = 0.014
TR = 0.864
TI = 0

PD = PDmap
T1 = T1map
T2 = T2map

""" PD = PDmap[200,6,40]
T1 = T1map[200,6,40]
T2 = T2map[200,6,40]

print("PD, T1 and T2",PD, T1, T2) # 0, 0, 0
print("type PD, T1 and T2",type(PD), type(T1), type(T2)) # <class 'numpy.float64'> <class 'numpy.float64'> <class 'numpy.float64'>

divide_zero = np.divide(-TE,0) # -inf
print(divide_zero)
print(type(divide_zero)) # <class 'numpy.float64'>
exp_divide_zero = np.exp(divide_zero)
print(exp_divide_zero) # 0
print(type(exp_divide_zero))  # <class 'numpy.float64'>      
print(np.abs(0*exp_divide_zero)) # 0
print(type(np.abs(0*exp_divide_zero))) # <class 'numpy.float64'> 

print(np.divide(-TE,T2)) # -inf
print(np.exp(np.divide(-TE,T2))) # 0
print(np.divide(-TI, T1)) # nan
print(np.exp(np.divide(-TI, T1))) #nan
print(np.divide(-TR, T1)) # -inf
print(np.exp(np.divide(-TR, T1))) # 0
print(1 - 2 * np.exp(np.divide(-TI, T1)) + np.exp(np.divide(-TR, T1)))
print(PD * np.exp(np.divide(-TE,T2)) * (1 - 2 * np.exp(np.divide(-TI, T1)) + np.exp(np.divide(-TR, T1)))) # nan
print(np.abs(PD * np.exp(np.divide(-TE,T2)) * (1 - 2 * np.exp(np.divide(-TI, T1)) + np.exp(np.divide(-TR, T1))))) # nan
print(np.abs(PD * np.exp(np.divide(-TE,T2)) * (1 - 2 * np.exp(-np.inf) + np.exp(np.divide(-TR, T1))))) # 0 """

signal_array = np.abs(PD * np.exp(np.divide(-TE,T2)) * (1 - 2 * np.exp(np.divide(-TI, T1)) + np.exp(np.divide(-TR, T1))))   

# replace all nan values with 0. Time how long it takes to replace all nan values with 0
import time
start_time = time.time()
signal_array = np.nan_to_num(signal_array)
print("--- %s seconds ---" % (time.time() - start_time)) # 

print(signal_array.shape) 
print(signal_array)
print(type(signal_array)) 
plt.imshow(signal_array[:,:,40], cmap='gray')
plt.show()