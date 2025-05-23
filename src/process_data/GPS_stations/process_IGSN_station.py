import pandas as pd
import os


FOLDER_INPUT = "../txt/"
# Load the CSV data into a DataFrame
df = pd.read_csv("IGSNetwork.csv")

# Display the first few lines of the DataFrame to check loading
print(df.head())

# xample of access to important columns
latitude = df["Latitude"]
longitude = df["Longitude"]
height = df["Height"]

header = """IGSN ground stations continuously collect high-precision GPS data, which is used for:

    Monitoring tectonic plate movements and crustal deformation
    Studying atmospheric conditions, including water vapor content
    Providing reference data for precise positioning applications
    Atmospheric and ionospheric studies,
   
    Here, the list of ground stations that you can use for have positions for analyse STEC 
    A STEC (Slant Total Electron Content) greater than 0.1 (in TECU units, which is 10^16 electrons/m²) 
    is often considered to indicate significant disturbances in the ionosphere. 

    When you read a STEC value from a file, you refer to the GPS ground station to determine the geographical region of the ionospheric disturbance.
    
"""

text = []
# Display specific information for verification
print("\nHere the coordonnates of GPS station  :")
for i, name in enumerate(
    df["#StationName"][:]
):  
    text.append(
        f"The earth station named {name[:4]} is at longitude: {longitude[i]}° and latitude: {latitude[i]}° and Height: {height[i]} meters,"
    )

with open(os.path.join(FOLDER_INPUT, f"ground_station_IGSN.txt"), "wb") as file:
    file.write(header.encode())
    file.writelines(element.encode() + b"\n" for element in text)

"""
for i, name in enumerate(df['#StationName'][:]):  # Afficher seulement les 5 premières stations
    print(f"\"{name[:4]}\",",end="")
"""
