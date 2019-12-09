#!/usr/bin/env python
# coding: utf-8

# # Section 1 : Reading a CSV and Create Point FeatureClass of Plot Data

# ## Step 1.
# **Import Python Modules**
#     - arc modules
#         - arcgis gives access to arcgis api
#         - arcpy gives access to eveything available in arcpro software (functions, layout etc.)
#     - other moduels
#         - pandas is used for data analysis and manipulation
#         - numpy also used for data analysis and manipulation (some pandas reliant on numpy)
#         - sodapy is a module recommended by CDC to use their API
#         - zipfile used to unzip zipfiles
#         - os gives access to basic functionalities of the computer (creating folders, path names, etc.)

# In[1]:


import arcgis
import arcpy
import pandas as pd
import numpy as np
import sodapy
from zipfile import ZipFile
import os
import json
import requests


# ## Step 2.
# **set up inputs to convert CSV to featureclass**

# In[2]:


# set up directory and geodatabase

space = arcpy.GetParameterAsText(0)
# space = "C:\\Users\\hjs5td\\Desktop"

incsv = arcpy.GetParameterAsText(1)
#"C:\\Users\\hjs5td\\Box Sync\\FIA Project\\FIA_Python\\plot_sample_9May19.csv"

# these are the names of longitude and latitude in your CSV 

longitude = arcpy.GetParameterAsText(2)
#'lon'

latitude = arcpy.GetParameterAsText(3)
#'lat'

plot_year = arcpy.GetParameterAsText(4) 
#"invyr"

usename = arcpy.GetParameterAsText(5)
#"hjs5td"
passwrd = arcpy.GetParameterAsText(6)
#"Hondoo12"

key = arcpy.GetParameterAsText(7)
#'a8240e46395d6100bb5585e555c6c5be99584107'

# ## Step 3.
# **create a geodatabase where we will store our data**

# In[3]:


outgdb = "AdvGIS_proj.gdb"
workspace = os.path.join(space, outgdb)

if arcpy.Exists(workspace):
    arcpy.Delete_management(workspace)

arcpy.CreateFileGDB_management(space,outgdb)

arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True


# ## Step 4.
# **create a featureclass from CSV**

# In[4]:


#define name of featureclass to go into geodatabase
plots = "plots"
plottab = "plot_table"

#GCS_WGS_1984 geographic coordinate system
sr = arcpy.SpatialReference(4326)

# web mercator
#sr = arcpy.SpatialReference(3857)

#USA_Contiguous_Albers_Equal_Area_Conic_USGS_version projected coordinate system
pr = arcpy.SpatialReference(102039) 

#from pyproj import Proj,transform

#arcpy.TableToTable_conversion(incsv,workspace,plottab)

#cursor = arcpy.da.UpdateCursor(plottab, [longitude,latitude])

#for row in cursor:
#    lon = row[0]
#    lat = row[1]
#    newsr = transform(Proj(init='epsg:3857'), Proj(init='epsg:4326'), lon, lat)
#    newlon = newsr[0]
#    newlat = newsr[1]
#    newrow = [newlon, newlat]
#    cursor.updateRow(newrow)
    
#del cursor

# assume WGS 1984

arcpy.XYTableToPoint_management(incsv,plots, x_field = longitude, y_field = latitude, coordinate_system = sr)


# In[5]:


## OR ##

# plotgpd = pd.read_csv(incsv)

# geometry = [Point(xy) for xy in zip(plotgpd[longitude], plotgpd[latitude])]
# plotgpd = plotgpd.drop([longitude,latitude], axis=1)

# # WGS_1984
# crs = {'init': 'epsg:4326'}

# # write GDF
# gdf = gpd.GeoDataFrame(plotgpd, crs=crs, geometry=geometry)

# # can write to a shapefile

#path = os.path.join(workspace,"plot_test.shp")

#gdf.to_file(path)


# ## Step 5.
# **create new feature class projected into equal area projection**

# In[6]:


plots_proj = 'plots_proj'

transformation = 'WGS_1984_(ITRF00)_To_NAD_1983'

#going from sr to pr coordinate system

arcpy.Project_management(plots, plots_proj, pr, transformation, sr)


# # Section 2 : Accessing APIS and Getting Explanatory Data

# # Download a Layer From ArcGIS hub
# http://hub.arcgis.com/pages/open-data

# ## Step 1.
# **Set up text inputs for accessing various API's**

# In[7]:


# inputs:

# username and password of arcgis account

# census key can be requested at : https://api.census.gov/data/key_signup.html 

key = 'a8240e46395d6100bb5585e555c6c5be99584107'


# ## Step 2. 
# **set up numeric variables to be used for PDSI API**

# In[8]:


# used in the sql clause for CDC API
# does not require a key or username+pass

minmonth = 6
maxmonth = 8
minyear = 1998


# ## Step 3.
# **get URL of a county feature layer from arcgis hub website.**

# In[9]:


URL = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized/FeatureServer/0/"
county_layer = arcgis.features.FeatureLayer(URL)
county_layer


# **you can use the code below to see what is allowed with this dataset; it says "extract" you can directly download the layer as shapefile. see https://developers.arcgis.com/python/guide/checking-out-data-from-feature-layers-using-replicas/**

# In[10]:


county_layer.properties.capabilities


# ## Step 4.
# **create a GIS() object; plot a map using the created GIS() object.** Need to create an account in order to download layers directly -- (my username and password are provided in the tool for simplicity)

# In[11]:


#gis1 = arcgis.gis.GIS(username=usename, password=passwrd)
#map1 = gis1.map("Missouri")
#map1


# In[12]:


## add to a map from a url

#map1.add_layer({"type":"FeatureLayer",
#                "url":URL,
#               })


# In[13]:


## print the names of the fields
#for f in county_layer.properties.fields:
#    print(f.name)


# ## Step 5.
# **query all features of the layer.**

# In[14]:


all_features = county_layer.query()

#print('Total number of rows in the dataset: ')
#print(len(all_features.features))


# ## Step 6. 
# **create spatial dataframe from the county_layer.**

# In[15]:


# store as dataframe pandas dataframe
# this works if we can extract the features


sdf = pd.DataFrame.spatial.from_layer(county_layer)

#View first 5 rows

print(sdf.head())


# **plot the spatial dataframe on the arcgis map, and print out the head.**

# In[16]:


#sdf.spatial.plot(map_widget=map1)


# ## Step 7. 
# **delete the columns that we do not need**

# In[17]:


print(list(sdf))


# In[18]:


keeperlist = ['FID', 'FIPS', 'OBJECTID', 'SHAPE', 'SQMI', 'STATE_FIPS', 'STATE_NAME', 'Shape_Area', 'Shape_Leng', 
              'Shape__Area', 'Shape__Length']

# FIPS = sdf.FIPS
# print(FIPS.head())

for i in list(sdf):
    if not i in keeperlist:
        del sdf[i]

print(list(sdf))     


# # Get and Format Drought Data
# https://open.cdc.gov/apis.html

# ## Step 8.
# **create a string that can take inputs of minimum year, minimum month and maximum month.**
# 

# In[19]:


# from our inputs ... this will control which months the drought data is gathered from (1-12 would get all months)
# I have set it to 6-8 because we have found that june through august is most important for forest conditions
# later on the palmer drought severity index values are averaged over these months

monthlist = list(range(minmonth,maxmonth+1))
final = str()
length = len(monthlist) - 1

for idx,i in enumerate(monthlist):
    if idx < length:
        string1 = "'{}',".format(i)
        final = final + string1
    else:
        string1 = "'{}'".format(i)
        final = final + string1
    
monthstring = " AND month IN ({})".format(final)

# minimum value for this clause is 1894
clause = "year > '{}'".format(minyear) + monthstring

print(clause)


# ## Step 9. 
# **Using sodapy library (recommended by CDC) get the drought data from CDC API.** set limit to something large so we get all records (if excluded will only get 1000).

# In[20]:


# this gets the pdsi data from cdc website using the query speciried in the get() function

client = sodapy.Socrata("data.cdc.gov", None)
results = client.get("en5r-5ds4", where=clause, limit = 10000000)
pdsi = pd.DataFrame.from_records(results)

client.close()


# In[21]:


print(pdsi.head(5))
print(len(pdsi))


# ## Step 10.
# **change datatypes of all columns.**

# In[22]:


# make sure all countyfips are stored as integers
# countyfips is used to join to the layer
# these are originally stored as text

intlist = ["countyfips","year","month","statefips"]

for i in list(pdsi):
    if i in intlist:
        pdsi[str(i)] = pd.to_numeric(pdsi[str(i)],downcast='integer')
    else:
        pdsi[str(i)] = pd.to_numeric(pdsi[str(i)],downcast='float')

    


# ## Step 11.
# **iterate through yearlist and store dataframes in dictionary.** merge all dataframes to one dataframe called all_drought.

# In[23]:



# get the maximum value from pdsi["year"] column
maxyear = max(pdsi["year"])

# min year plus one because we used > min year not => minyear
# we will iterate through this list and use values as keys/column names

yearlist = list(range(minyear+1,maxyear+1))

# create dictionary to easily store dataframes as we iterate
D = {}

# enumerate the list so we can know when we are on the first iteration (see below)

for idx,i in enumerate(yearlist):
    # get values where year == i
    D[i] = pdsi[pdsi.year == i]
    # monthlist defined in step 8
    D[i] = D[i][D[i].month.isin(monthlist)]
    # groupby county and find the average pdsi across the months in our list
    D[i] = D[i].groupby(['countyfips'])[['pdsi']].mean().reset_index()
    # get a string of the value in yearlist
    yearsuf = str(i)
    # create a column name
    pdsiname = "pdsi{}".format(yearsuf)
    # reassign the column name to the PDSI column
    D[i] = D[i].rename(columns={'pdsi': pdsiname})
    # if it is the first iteration than store the dataframe as all_drought
    if idx == 0:
        all_drought = D[i]
    # otherwise merge the dataframes on the county number
    else:
        all_drought = all_drought.merge(D[i], how='inner', on='countyfips')
    # print(len(all_drought))

del D


# In[24]:


print(all_drought.head())


# ## Step 12.
# **Make sure that FIPS in the spatial dataframe is stored as an integer. Then merge the drought data to the county data using the countyfips and FIPS keys.**

# In[25]:


sdf['FIPS'] = pd.to_numeric(sdf['FIPS'],downcast='integer')


# In[26]:


pdsicounty = sdf.merge(all_drought, how='inner', left_on='FIPS', right_on='countyfips')


# In[27]:


print(pdsicounty.head())


# In[28]:


print(list(pdsicounty))


# ## Step 13.
# **write our merged spatial dataframe to a feature class.**  store it in the geodatabase.

# In[29]:


pdsipath = os.path.join(workspace,"pdsi")

pdsicounty.spatial.to_featureclass(location = pdsipath)


# # Get and Download Population Data

# ## Step 14.
# **access the census API for county level population estimates using for years 2000 to 2010**

# In[30]:


## see https://api.census.gov/data/2000/pep/int_population/examples.html ##

# this gets county level population estimates from 2000 to 2010

URL = "https://api.census.gov/data/2000/pep/int_population?get=COUNTY,DATE_DESC,POP,GEONAME&for=county:*&in=state:*&key={}".format(key)

data = requests.get(URL)

data


# ## Step 15.
# **convert json to nested list using the json() function**

# In[31]:


datajson = data.json()


# ## Step 16.
# **use pandas to write a dataframe from the datajson list**

# In[32]:


cp = pd.DataFrame.from_records(datajson)


# In[33]:


print(cp.head())
print(len(cp))


# In[34]:


list(cp)


# ## Step 17.
# **make the first row the coulumn names and drop that row**

# In[35]:


cp.columns = cp.iloc[0]
cp = cp.reindex(cp.index.drop(0))


# In[36]:


print(list(cp))
print(len(cp))


# In[37]:


print(cp.head())


# ## Step 18.
# **do the same thing for county level data from 2010 to 2018**

# In[38]:



# if we do not include "DATE_CODE" than we only get the 2018 estimate
URL = "https://api.census.gov/data/2018/pep/population?get=COUNTY,DATE_CODE,DATE_DESC,POP,GEONAME&for=county:*&in=state:*&key={}".format(key)

data = requests.get(URL)

datajson = data.json()


# In[39]:


ncp = pd.DataFrame.from_records(datajson)

ncp.columns = ncp.iloc[0]
ncp = ncp.reindex(ncp.index.drop(0))

# delete DATE_CODE
del ncp["DATE_CODE"]


# ## Step 19. 
# **concatenate the two dataframes (stack them on top of one another); must have same columns; reset the index so that all values are unique and delete the old index column**

# In[40]:


# since we redefine cp here make sure that we rerun the first request sequence before we concatanate dataframes again

cp = pd.concat([ncp,cp], axis=0, sort = False, join='outer',ignore_index=True)


# In[41]:


cp = cp.reset_index()


# In[42]:


del cp["index"]


# ## Step 20. 
# **iterate through the indexes of the cp dataframe to format the FIPS and year variables.** I tried usiung datetime package but it was simpler to just format it on my own.

# In[43]:


stringlist = ["population estimate", "population estimates base","Census 2010 population","Census population"]

# create an empty column year
cp["year"] = ""
#create an empty column FIPS
cp["FIPS"] = ""
#create an empty list to store year values
yearlist = list()

# iterate through the indexs
# iterating through a pandas dataframe
for i in cp.index:
    datestr = cp.at[i,"DATE_DESC"]
    county = str(cp.at[i,"county"])
    state = str(cp.at[i,"state"])
    FIPS = int(state + county)
    cp.at[i,"FIPS"] = FIPS
    # if any(x in datestr for x in stringlist):
    for y in stringlist:
        # check to see if datestr created above ends with any value in the list
        if datestr.endswith(y):
            # get the length of the text that the datestr endswith
            length = len(y)
            # create a negative integer value from that length
            position = -length
            # new string excluding that text
            new_datestr = datestr[:position]
            # new string excluding month and day
            # includes the space and the year I beleive
            new_year = new_datestr[-5:]
            # convert to integer
            year = int(new_year)
            # assign value
            cp.at[i,"year"] = year
            # to check the min and max later on
            yearlist.append(year)

# we need to drop duplicates because each county includes a baseline 2000 census estimate and an additional 2000 estimate
# I sort values so that we are always dropping the baseline estimate
            
cp = cp.sort_values(['state','county','year'], axis=0, ascending=True,kind='quicksort', na_position='first')

cp = cp.drop_duplicates(subset=['state','county','year'], keep='last', inplace=False)   

print(cp.head())
print(cp)


# ## Step 21.
# **create a new list of the minimum year and the maximum years found in the dataframe**

# In[44]:


yeararray = np.array(yearlist)

x = min(yeararray)
y = max(yeararray)

yearlist = list(range(x,y+1))

del yeararray
print(list(cp))


# ## Step 22.
# **select rows by year; rename column; mrege dataframes (same as drought method)**

# In[45]:


D = {}

for idx,i in enumerate(yearlist):
    print(i)
    D[i] = cp[cp.year == i]
    # groupby county and find the average pdsi
    yearsuf = str(i)
    name = "pop{}".format(yearsuf)
    D[i] = D[i].rename(columns={'POP' : name})
    if idx == 0:
        all_pop = D[i]
    else:
        # get a subselection of columns
        D[i] = D[i][[name, 'FIPS']]
        print(list(D[i]))
        all_pop = all_pop.merge(D[i], how='inner', on='FIPS')
    #print(len(all_pop))
    #print(idx)


# ## Step 23.
# **merge pop data to spatial dataframe**

# In[46]:


popcounty = sdf.merge(all_pop, how='inner', on='FIPS')
list(popcounty)


# ## Step 24.
# **write population data to geodatabse**

# In[47]:


poppath = os.path.join(workspace,"pop")


popcounty.spatial.to_featureclass(location = poppath)


# ## Step 25.
# **Spatial Joins of Point**
# 
# https://developers.arcgis.com/python/guide/spatially-enabled-dataframe-advanced-topics/#Spatial-Joins

# In[48]:


arcpy.MakeFeatureLayer_management(plots_proj, 'tempplots')
arcpy.MakeFeatureLayer_management(pdsipath, 'temppdsi')
arcpy.MakeFeatureLayer_management(poppath, 'temppop')


# In[49]:


orig = arcpy.ListFields('tempplots')
origlist = list()


for i in orig:
    x = i.name
    origlist.append(x)


# In[50]:


temp = "temporaryjoin"

arcpy.SpatialJoin_analysis('tempplots','temppop',temp, join_operation = 'JOIN_ONE_TO_ONE', join_type = 'KEEP_ALL', match_option = 'CLOSEST')


# In[51]:


temp1 = "temporatyjoin1"

arcpy.SpatialJoin_analysis(temp,'temppdsi',temp1, join_operation = 'JOIN_ONE_TO_ONE', join_type = 'KEEP_ALL', match_option = 'CLOSEST')


# In[52]:


pltdf = pd.DataFrame.spatial.from_featureclass(temp1)


# In[53]:


deletelist = ['OBJECTID',
 'Join_Count',
 'TARGET_FID',
 'Join_Count_1',
 'TARGET_FID_1',
 'Field1',
 'FID_1',
 'FIPS_1',
 'SQMI_1',
 'STATE_FIPS_1',
 'STATE_NAME_1',
 'Shape_Leng_1',
 'Shape__Area_1',
 'Shape__Length_1',
 'countyfips',
 'STATE_FIPS',
 'STATE_NAME',
 'Shape_Leng',
 'Shape__Area',
 'Shape__Length',
 'COUNTY',
 'DATE_DESC','FID']

for i in deletelist:
    if hasattr(pltdf, i):
        del pltdf[i]

list(pltdf)


# In[54]:


yearlist = list(range(2000,2018))
columnlist = list(pltdf)

pltdf['final_pdsi'] = ""
pltdf['final_pop'] = ""

for i in pltdf.index:
    popstr = str(int(pltdf.at[i,plot_year]))
    pdsistr = str(int(pltdf.at[i,plot_year]) - 1)
    for y in columnlist:
        if popstr in y:
            if y.startswith('pop'):
                pltdf.at[i,"final_pop"] = pltdf.at[i,y]
        elif pdsistr in y:
            if y.startswith('pdsi'):
                pltdf.at[i,"final_pdsi"] = pltdf.at[i,y]

    


# In[55]:


newlist = ['FIPS','SQMI','final_pdsi','final_pop']
for i in newlist:
    origlist.append(i)


# In[56]:


for y in list(pltdf):
    if not y in origlist:
        del pltdf[y]


# In[57]:


pltdf['final_pop'] = pd.to_numeric(pltdf['final_pop'],downcast='float')
pltdf['SQMI'] = pd.to_numeric(pltdf['SQMI'],downcast='float')

pltdf.loc[:,'poparea'] = pltdf.final_pop / pltdf.SQMI


# In[58]:


plotpath = os.path.join(workspace,"update_plots")
csvpath = os.path.join(space,"SudekumPlotSampleUpdate.csv")

pdsicounty.spatial.to_featureclass(location = plotpath)
pltdf.to_csv(csvpath)

