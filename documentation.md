1) Trying to understand the data and how its stored. Upon research I found out the ERA5 dataset is around 5 petabytes and that's why its hosted on google cloud.

2) What is zarr ?  A file format specifically for storing large multidimensional arrays stored in the cloud. The use of this is traditional formats like NetCDF were not designed for cloud access and to read one small chunk we will have to download the whole source but with zarr data is split into chunks of arrays and stored remotely and can be accessed as we need. 

On noticing furhter each weather variable gets its own folder , and each folder contains atleast these 2 files 
1) .zarray : techniacal Metadata 
what is 1*721 * 1440  : this is the shape of the array , 1 time dimenstion 721 latitude points * 1440 longititude points. 

so basically for every time there is a grid of 721 horizontal lines and 1440 vrtical lines expressing the world and at each intersection of these grids there is a number which represnets the sea surface temperature 

The time period in which this takes a snapshot is 6 hours pretty intuitive from the file name 
https://storage.googleapis.com/gcp-public-data-arco-era5/ar/1959-2022-6h-1440x721.zarr/high_vegetation_cover/.zarray
 every 6 hours from 1959 to 2022.
 THe number of 1440 * 721 refers to the dimentsions of the world expressed as a 2d grid with 1440 veritcal lines ( longtitudes) and 721 horizontal lines ( latitudes)

 The variable i am picking is the sea-surface-temperature  which is basically the temperature of just the surface of the sea , the temperature of the area where the ocean meets the air.
 Common abbreviation  : sst 
 Sea surface temperature is a single-level variable as it only exists at the surface the sea.


# making the actual visualisation 

step-1 : figuring out how to access the data.
just asked claude on how to access the data. 
Need to access three libraries : 
1) gcsfs : to talk to GCS 
2) zarr : reading the zarr format 
3) xarray : standard library to work with mutidimensional data.
