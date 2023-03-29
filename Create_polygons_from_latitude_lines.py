#Import the modules pandas, geopandas and shapely
import pandas as pd
import geopandas as gpd
import shapely as sh

#Read both shapefiles in as geodataframes
directory = "C:/Users/Azzla/Downloads/"
input_shp = "Country_Extents.shp"
gdf_world = gpd.read_file(directory + input_shp)

directory = "C:/Users/Azzla/Downloads/"
input_shp = "WA_Latitude_Extents.shp"
gdf_wa = gpd.read_file(directory + input_shp)

#Create array to store all latitude values
AllLatitudes = []

#Create array to store all countries to south of latitude line
AllCountries = []

#Extract latitude values from WA longitude lines
lat_min_bounds = gdf_wa['geometry'][0].bounds
lat_min = lat_min_bounds[1]
lat_max_bounds = gdf_wa['geometry'][1].bounds
lat_max = lat_max_bounds[1]


#Extract countries that are to the south of the latitude line
countries = gdf_world['C_toSouth']

#Extract all latitude values from the same geodataframe
for i in range(len(countries)):
    lat_line_bounds = gdf_world['geometry'][i].bounds
    latitude = lat_line_bounds[1]
    if latitude >= lat_max:
        latitude = lat_max
        AllLatitudes.append(latitude)
        country = countries[i]
        AllCountries.append(country)
    elif latitude <= lat_min:
        latitude = lat_min
        AllLatitudes.append(latitude)
        country = countries[i]
        AllCountries.append(country)
    else:
        AllLatitudes.append(latitude)
        country = countries[i]
        AllCountries.append(country)

#Create a new dataframe to store AllLatitudes and AllCountries values
df_lat = pd.DataFrame({'country': AllCountries, 'latitude': AllLatitudes})

#Sort new dataframe by latitudes, lowest to highest
df_lat_sorted = df_lat.sort_values('latitude', ignore_index=True)

#Now create the polygons using shapely. The country represented by the polygon is
#The second polygon
#Start off with creating an array to store the shapely geometry
AllPolygons = []
AllCountriesInPolygons = []

for i in range(1, len(df_lat['latitude'])):
    lower_latitude = df_lat_sorted['latitude'][i-1]
    upper_latitude = df_lat_sorted['latitude'][i]
    country = df_lat_sorted['country'][i]
    poly = sh.geometry.Polygon([[-180, upper_latitude], [180, upper_latitude], [180, lower_latitude], [-180, lower_latitude]])
    AllPolygons.append(poly)
    AllCountriesInPolygons.append(country)

#Now create a dataframe for the polygons
df_polygons = pd.DataFrame({'country': AllCountriesInPolygons, 'geometry': AllPolygons})

#Create a geodataframe from the dataframe
gdf_polygons = gpd.GeoDataFrame(AllCountriesInPolygons, geometry=df_polygons.geometry)

#Make sure the columns are the right name
gdf_polygons.columns = ['country', 'geometry']

#Now export geodataframe to shapefile, ready for mapping in QGIS (or ArcGIS or whatever mapping platform is available)
output = "Countries_DirectlyWestOfWA.shp"
gdf_polygons.to_file(directory + output)
print('Complete')


    
    
               

        
    
