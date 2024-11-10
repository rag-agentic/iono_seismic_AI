import pandas as pd
import os
import sys 

FILENAME_INPUT='../../../raw_data/seismics/seismics_flare_06_09_2017.csv'
FOLDER_OUTPUT='../../../documents_to_RAG/'  
FILENAME_OUTPUT='summaries_seismics_flare_06_09_2017.txt'

# Read the file with the correct separator and decimal settings
df = pd.read_csv(FILENAME_INPUT, 
                 sep=";", 
                 decimal=",", 
                 parse_dates=["date (UTC)"], 
                 dayfirst=True)

# Function to generate the summary
def generate_summary(row):
    # Extract information from the row
    date = row['date (UTC)'].strftime('%Y-%m-%d %H:%M:%S')
    latitude = row['latitude (deg)']
    longitude = row['longitude (deg)']
    magnitude = row['magnitude']
    depth = row['profondeur (km)']
    location = row['lieu']
    
    # Create the summary text
    summary = f"On {date}, at a longitude of {longitude}° and latitude of {latitude}°, " \
              f"a magnitude {magnitude} earthquake occurred at a depth of {depth} km near {location}."
    return summary

df = df.sort_values(by='date (UTC)', ascending=True)

# Apply the function to each row of the DataFrame
df['summary'] = df.apply(generate_summary, axis=1)

# Afficher les résumés
print("\n".join(df['summary']))


with open(os.path.join(FOLDER_OUTPUT,FILENAME_OUTPUT), "a") as file:
    file.write("\n".join(df['summary']))
    print(f"Data successfully saved as {FILENAME_OUTPUT}")
