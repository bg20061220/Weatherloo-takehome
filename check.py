import pickle
import numpy as np

with open('sst_data.pkl', 'rb') as f:
    data = pickle.load(f)

print(f"Shape: {data['sst'].shape}")
print(f"Timestamps: {data['time'][0]} → {data['time'][-1]}")
print(f"Temp range: {np.nanmin(data['sst']):.1f}°C to {np.nanmax(data['sst']):.1f}°C")
print(f"Num snapshots: {len(data['time'])}")