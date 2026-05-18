import pickle

with open('sst_data.pkl', 'rb') as f:
    data = pickle.load(f)

print(data.keys())