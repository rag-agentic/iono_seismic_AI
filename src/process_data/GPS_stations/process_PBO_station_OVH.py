import pandas as pd
import os
import json


FOLDER_OUTPUT='../../summaries_documents/txt/'
FILENAME='../json/ionosphere/stations_PBO_OVH.json'


data_json = pd.read_json(FILENAME)

# # Extract features and convert them to DataFrame
df = pd.json_normalize(data_json['features'])

# Separate coordinates into separate columns
df['longitude'] = df['geometry.coordinates'].apply(lambda x: x[0])
df['latitude'] = df['geometry.coordinates'].apply(lambda x: x[1])
df['name_id'] = df['properties.pnum']
df['network'] = df['properties.stntype']
print(df.head())

header="""Plate Boundary Observatory (PBO) OVH ground stations continuously collect high-precision GPS data, which is used for:

    Monitoring tectonic plate movements and crustal deformation
    Studying atmospheric conditions, including water vapor content
    Providing reference data for precise positioning applications
    Atmospheric and ionospheric studies,
   
    Here, the list of ground stations that you can use for have positions for analyse STEC 
    A STEC (Slant Total Electron Content) greater than 0.1 (in TECU units, which is 10^16 electrons/m²) 
    is often considered to indicate significant disturbances in the ionosphere. 

    When you read a STEC value from a file, you refer to the GPS ground station to determine the geographical region of the ionospheric disturbance.
    Here you can find a list of earth ground station used for all measure for STEC.
"""

for iname_id,long,lat in zip(df['name_id'],df['longitude'],df['latitude']):
    print(iname_id,long,lat)

   
text= [ ]
 
print("\nHere the coordonnates of GPS station  :")
for iname_id,long,lat in zip(df['name_id'],df['longitude'],df['latitude']):
    print(iname_id,long,lat)
    #text.append(f"The earth station named {iname_id} is at longitude: {long:.2f}° and latitude: {lat:.2f}°")
    text.append(f"The ground station named {iname_id} is located at GPS coordinates {long:.2f}° degrees longitude and {lat:.2f} degrees latitude.")

with open(os.path.join(FOLDER_OUTPUT,f"ground_station_PBO_OVH.txt"), "wb") as file:
    file.write(header.encode())
    file.writelines(element.encode() + b'\n' for element in text)
    print("File written to disk")


for name in  df['name_id']:   
    print(f"\"{name}\",",end="")
