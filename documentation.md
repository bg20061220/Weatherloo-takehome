
# Answers : 
1)  An ELI5-style explanation of what it represents physically  & Common abbreviation 
   Ans : The variable i am picking is the sea-surface-temperature  which is basically the temperature of just the surface of the sea , the temperature of the area where the ocean meets the air.
  Common abbreviation  : sst 
2) Whether it's a single-level variable (e.g. surface temperature) or one associated with pressure levels (e.g. wind at different altitudes in the atmosphere)
   Ans :  Sea surface temperature is a single-level variable as it only exists at the surface the sea.

3)  What is the time step of the dataset? ("How often does this dataset take a snapshot of the world?")
  Ans : Every 6 hours.

4) What timezone/time standard does the dataset use?
   Ans : UTC 

5)  What do the numbers 1440x721 refer to? 
    Ans :  THe number of 1440 * 721 refers to the dimentsions of the world expressed as a 2d grid with 1440 veritcal lines ( longtitudes) and 721 horizontal lines ( latitudes)

6) What is zarr ? 
   Ans : A file format specifically for storing large multidimensional arrays stored in the cloud. The use of this is traditional formats like NetCDF were not designed for cloud access and to read one small chunk we will have to download the whole source but with zarr data is split into chunks of arrays and stored remotely and can be accessed as we need.  

1) Trying to understand the data and how its stored. Upon research I found out the ERA5 dataset is around 5 petabytes and that's why its hosted on google cloud.


# Acutal Documentation of the Project + Design Choices. 

On noticing furhter each weather variable gets its own folder , and each folder contains atleast these 2 files 
1) .zarray : techniacal Metadata 
what is 1*721 * 1440  : this is the shape of the array , 1 time dimenstion 721 latitude points * 1440 longititude points. 

so basically for every time there is a grid of 721 horizontal lines and 1440 vrtical lines expressing the world and at each intersection of these grids there is a number which represnets the sea surface temperature 


# making the actual visualisation 

step-1 : figuring out how to access the data.
just asked claude on how to access the data. 
Need to access three libraries : 
1) gcsfs : to talk to GCS 
2) zarr : reading the zarr format 
3) xarray : standard library to work with mutidimensional data.

Dataset preview <xarray.Dataset> Size: 41TB
 

# Visualization Choice 
1) Choosing to make a grid 2d map to represent the sst , a simple quick to build and intuitive way of presenting the change in sst. Will use plotly to make the map.
2) Adding a slider for time , can be shifted to view the difference in sst over time easily.
3) Picked 20 dec 2006 cause that's my birthday.

4) Features that would make it more helpful but not adding since its an MVP takehome kinda thing 
  a) More visual panels providing insights like , which region had the most change , change by the tiem of dat , average sst by time. 

5) Choosing to break the down the latitude and longitudes by /4 , to reduce the burden and make the render faster as well , as doing has almost no effects on 
the quality of the visualization. 
6) Will host this on github pages.
7) Converted Kelvin to celcius since its what's commonly used.
8) Looked at the dataset and found the max and min data points to make the colors comparable over time.

# HOW I used AI in this 
1) asked how to access the data from gcs , it told me about libraries liek gcsfs and xarray. 
2) Asked it to use Plotly to create a  heatmap with all the design choices , prompt was 

""" Help me build an intearctive sea surface temp visualiaztion from the ERA5 data of 20 snapshots from Dec 20 2006 00:00 UTC , every 6 hours , also convert kelvin to celcius , divide the lat and longs by 4 to optimize for performance, download only the needed data and save the data
to .pkl file for not downloading everytime and a generate a simple html.file which is host ready for github pages.  for the visualisation also add a slider to go through time which is manual only , also add a input dialog box where i can pin point a specifc point on the map."""

THis was not all a single prompt but what i built by reiterating it multiple times and did changes that made the visual better.

# Approach to solving the problem 
Understanding the dataset -> picking a variable -> looking if its single variable or not -> figuring out min and max values for color comparison -> choosing the actual visual layer whether a map or a globe , choose map as its fast and reliable and intuitive -> figure out all the specifications of the map and ask claude to create from it and then refine it based on the features i want untill the marginal benefit of adding features almost dies. 

