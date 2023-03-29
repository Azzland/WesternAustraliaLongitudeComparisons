#Import the modules Geopandas, Pandas and Shapely
import pandas as pd
import geopandas as gpd
import shapely as sh

#Load the shapefile containing all the countries of the world (World.shp)
#using Geopandas, which loads it as a geodataframe
directory = "C:/Users/Azzla/Downloads/"
input_shp = "Countries/World.shp"
gdf_world = gpd.read_file(directory + input_shp)

#Load the shapefile containing the Australian states and territories using
#geopandas in similar fashion
directory = "C:/Users/Azzla/Downloads/"
input_shp = "STE_2021_AUST_SHP_GDA2020/STE_2021_AUST_GDA2020.shp"
gdf_aust = gpd.read_file(directory + input_shp)

#For the world.shp, it's noteable that each feature is multipolygon
#These features will be changed to polygon
#To do that the explode function in geopandas can be employed
gdf_world_poly = gdf_world.explode(index_parts=True)

#Now for each feature in that shapefile, lets get the minimum and maximum
#latitude. To do this we find the min and max latitude and longitudes by
#using the bounds function with the geometry features of the geodataframe
geom = gdf_world_poly['geometry']
geom_extents = geom.bounds

#From geom_extents we can extract the minimum and maximum latitudes
lat_min = geom_extents['miny']
lat_max = geom_extents['maxy']

#Get all the countries names from the geodataframe
countries = gdf_world_poly['name']

#Now we only want the countries directly across from Western Australia, so on the other
#side of the Indian Ocean
#Need to manually check a map
#This will include South American countries possibly south of the
#southernmost point of the African landmass
OtherSideOfIndian = []
OtherSideOfIndian.append('South Africa')
OtherSideOfIndian.append('Mauritius')
OtherSideOfIndian.append('Reunion')
OtherSideOfIndian.append('Madagascar')
OtherSideOfIndian.append('Tanzania')
OtherSideOfIndian.append('Mozambique')
OtherSideOfIndian.append('Kenya')
OtherSideOfIndian.append('Uruguay')
OtherSideOfIndian.append('Argentina')
OtherSideOfIndian.append('Brazil')

#Create two arrays, one to store the minimum latitudes and one to store
#the maximum latitudes
MinLatitudes = []
MaxLatitudes = []
CountriesOtherSide = []

def country_check(country, listcountries):
    ctry_check = False
    for c in listcountries:
        if c == country:
            ctry_check = True
    return ctry_check

#First let's check to see if all the countries are in World.shp
n = 0
for ctry in OtherSideOfIndian:
    ctry_check = country_check(ctry, countries)
    if ctry_check == False:
        while ctry_check == False:
            string = str(ctry) + ' is not in the shapefile'
            string_two = 'List of countries'
            print(string)
            print(string_two)
            print(countries)
            string_three = 'Enter the name in the shapefile that best represents ' + str(ctry)
            country = input(string_three)
            OtherSideOfIndian[n] = country
            ctry = country
            ctry_check = country_check(ctry, countries)
    n += 1

#Loop through the list of countries to find those who are on the other side
#of the Indian Ocean to WA. If they are take their row location because that will
#identify their maximum and minimum longitudes     
for i in range(len(countries)):
    if countries.iloc[i] in OtherSideOfIndian:
        MinLatitudes.append(lat_min.iloc[i])
        MaxLatitudes.append(lat_max.iloc[i])
        CountriesOtherSide.append(countries.iloc[i])

#Now for the Australian states shapefile we only want the extents for Western Australia
geom_aus = gdf_aust['geometry']
geom_extents_aus = geom_aus.bounds
lat_min_aus = geom_extents_aus['miny']
lat_max_aus = geom_extents_aus['maxy']
state_names = gdf_aust['STE_NAME21']

for i in range(len(state_names)):
    if state_names.iloc[i] == 'Western Australia':
        row_wa = i
MinLatitudeWA = lat_min_aus.iloc[row_wa]
MaxLatitudeWA = lat_max_aus.iloc[row_wa]

#Now loop through all the countries possibly directly on other side of ocean from WA
#If their minimum latitude is greater than the maximum latitude of WA
#Or their maximum latitude is less than the minimum latitude of WA
#Don't create lines and add them to the dataframe
#Otherwise, all clear to add to dataframe
LatitudesFinal = []
CountriesOtherSideFinal = []
MinOrMax = []


for i in range(len(CountriesOtherSide)):
    if (MinLatitudes[i] > MaxLatitudeWA) or (MaxLatitudes[i] < MinLatitudeWA):
        pass
    else:
        latmin = MinLatitudes[i]
        latmax = MaxLatitudes[i]
        line_min = sh.geometry.LineString([[-180, latmin], [0, latmin], [180, latmin]])
        line_max = sh.geometry.LineString([[-180, latmax], [0, latmax], [180, latmax]])
        LatitudesFinal.append(line_min)
        MinOrMax.append('min')
        CountriesOtherSideFinal.append(CountriesOtherSide[i]) 
        LatitudesFinal.append(line_max)
        MinOrMax.append('max')
        CountriesOtherSideFinal.append(CountriesOtherSide[i])

#Now create latitude lines for WA extent
WAlatmin = sh.geometry.LineString([[-180, MinLatitudeWA], [0, MinLatitudeWA], [180, MinLatitudeWA]])
WAlatmax = sh.geometry.LineString([[-180, MaxLatitudeWA], [0, MaxLatitudeWA], [180, MaxLatitudeWA]])
WALines = [WAlatmin, WAlatmax]
WAMinOrMax = ['min', 'max']

#Create the dataframe for the WA latitude min and max lines then write to shapefile        
wa_df = pd.DataFrame({'min_max':WAMinOrMax, 'geometry':WALines})
western_australia_lat = gpd.GeoDataFrame(WAMinOrMax, geometry=wa_df.geometry)
western_australia_lat.columns = ['min_max', 'geometry']

output = "WA_Latitude_Extents.shp"
western_australia_lat.to_file(directory + output)


#Create the dataframe for the latitude min and max lines for the countries then write to shapefile        
c_df = pd.DataFrame({'name': CountriesOtherSideFinal, 'geometry':LatitudesFinal})
countries_lat = gpd.GeoDataFrame(CountriesOtherSideFinal, geometry=c_df.geometry)
countries_lat.columns = ['name', 'geometry']

output = "Country_Extents.shp"
countries_lat.to_file(directory + output)

print('Complete!')

#Shapefiles can be checked and edited manually in QGIS Or ArcGIS

