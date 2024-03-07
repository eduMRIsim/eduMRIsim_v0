import numpy as np

# Set the lower limit for random values (e.g., 0.1)
lower_limit = 0.1

# Assuming you have already defined m, n, p
m, n, p = 5, 5, 5

# Generate random arrays with values greater than zero
PD = np.random.uniform(lower_limit, 1, size=(m, n, p))
T1 = np.random.uniform(lower_limit, 1, size=(m, n, p))
T2 = np.random.uniform(lower_limit, 1, size=(m, n, p))

# TE, TI, and TR are scalars
TE = 0.1
TI = 0.2
TR = 0.3

signal_array = np.abs(PD * np.exp(np.divide(-TE, T2)) * (1 - 2 * np.exp(np.divide(-TI, T1)) + np.exp(np.divide(-TR, T1))))

print(f"Size using np.shape(): {np.shape(signal_array)}")
