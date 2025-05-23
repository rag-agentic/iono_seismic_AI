import pandas as pd
import os
import sys 
import json


"""
FILENAME_INPUT='../../../raw_data/seismics/seismics_06_02_2023.json'
"""
FILENAME_INPUT='../../../raw_data/seismics/seismics_egee_30_10_2020.json'
FOLDER_OUTPUT='../../../documents_to_RAG/' 
FILENAME_OUTPUT='summaries_seismics_30_10_2020.txt'

with open(FILENAME_INPUT, 'r') as file:
    data = json.load(file)

# Extract data from the "features" key and normalize it
df = pd.json_normalize(data['features'])

# Extract only the columns of interest
df = df[['properties.mag', 'properties.place', 'properties.time', 'geometry.coordinates']]

# Rename columns for clarity
df.columns = ['magnitude', 'place', 'timestamp', 'coordinates']

# Convert timestamp to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
#df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Split coordinates into latitude and longitude
df[['longitude', 'latitude', 'depth']] = pd.DataFrame(df['coordinates'].tolist(), index=df.index)

# Generate text description for each row
df['description'] = df.apply(lambda row: f"On {row['timestamp']}, there was an earthquake of magnitude {row['magnitude']} at {row['place']}, located at GPS coordinates ({row['latitude']}, {row['longitude']}).", axis=1)

# Write descriptions to a text file
with open(os.path.join(FOLDER_OUTPUT,FILENAME_OUTPUT), "w") as file:
    for description in df['description']:
        file.write(description + "\n")
