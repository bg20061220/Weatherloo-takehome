import xarray as xr 
import gcsfs 
import numpy as np 
import pickle 

fs  = gcsfs.GCSFileSystem(token='anon')
store = fs.get_mapper('gcp-public-data-arco-era5/ar/1959-2022-6h-1440x721.zarr')
ds = xr.open_zarr(store , consolidated=True)

print("Coonnected , Getting the sst")
sst = ds['sea_surface_temperature']

# Getting the 20 snapshots 
start = '2006-12-20T00:00'
end = '2006-12-24T18:00'
sst_window = sst.sel(time=slice(start , end))

print("Loading snapshots")
sst_loaded = sst_window.load() 

sst_celcius = sst_loaded - 273.15
sst_celcius.attrs['units'] = 'C'

# saving data to disk 

data = {
    'sst' : sst_celcius.values , 
    'lat' : sst_celcius.latitude.values , 
    'long' : sst_celcius.longitude.values , 
    'time' : [str(t)[:16] for t in sst_celcius.time.values] , 
}

with open('sst_data.pkl', 'wb') as f:
    pickle.dump(data, f)
 
print("Saved to sst_data.pkl")
