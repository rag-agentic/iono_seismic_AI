import netCDF4
import xarray as xr
import pandas as pd
import sys
import os

# Ouvrir le fichier NetCDF
FOLDER_INPUT = "../../../raw_data/TEC/global_TEC_5_mai_2024/2024051009_atec.nc"
FILENAME_OUTPUT = "../../../documents/summaries_storm_iono_5_mai_2024.txt"


def classify_normalized_stec(value):
    if abs(value) < 20:
        return None
    elif abs(value) > 20 and abs(value) < 30:
        return "light disturbances"
    elif abs(value) > 30 and abs(value) < 35:
        return "moderate disturbances"
    elif abs(value) > 35 and abs(value) < 50:
        return "strong disturbances"
    elif abs(value) > 50 and abs(value) < 100:
        return "extreme disturbances"
        # Fonction de standardisation


def summaries(df_cleaned):
    summaries = []

    hourly_stats = (
        df_cleaned.groupby("hour")
        .agg(
            atec_mean=("atec", "mean"),
            atec_std=("atec", "std"),
            atec_min=("atec", "min"),
            atec_max=("atec", "max"),
            lat_mean=("lat", "mean"),
            lon_mean=("lon", "mean"),
        )
        .reset_index()
    )

    print(hourly_stats)

    for index, row in hourly_stats.iterrows():
        hour = row["hour"]
        mean = row["atec_mean"]
        std = row["atec_std"]
        max = row["atec_min"]
        min = row["atec_max"]
        lon = row["lon_mean"]
        lat = row["lat_mean"]

        str_classify_value = classify_normalized_stec(mean)
        if str_classify_value is not None:
            first_date = df["time"].dt.strftime("%Y-%m-%d")
            # Fromat text
            time_str = f"{hour}h"
            # Building text to summaries
            text = f"On {first_date} ,from {time_str} to {hour+1}h the measure of ATEC {mean:.2f} , located at GPS coordinates latitude = ({lat:.2f}, longitude = {lon:.2f} is {str_classify_value} with max = {max:2f} and min = {min:2f})."

            summaries.append(text)
            print(summaries)
    return summaries


# Open the NetCDF file using xarray
file_path = FOLDER_INPUT  # Replace with your actual file path

dataset = xr.open_dataset(file_path)
df = dataset.to_dataframe()
df = df.reset_index()
print(df.columns.tolist())


df = df.drop("latitude", axis=1)
df = df.drop("longitude", axis=1)
df["hour"] = df["time"].dt.hour

print(df.head())
df.columns = ["time", "lat", "lon", "atec", "hour"]

# Convertir la colonne 'time' en format datetime
df["time"] = pd.to_datetime(df["time"])
# df['hour'] = df['time'].dt.hour

print(df.head())


df_cleaned = df.dropna()

# Générer la description en texte pour chaque ligne
df_cleaned["description"] = df_cleaned.apply(
    lambda row: f"On {row['time']} This is a measure of ATEC {row['atec']:.2f} , located at GPS coordinates latitude = {row['lat']:.2f}, longitude = {row['lon']:.2f}.",
    axis=1,
)

print(df_cleaned["description"])

# Écrire les descriptions dans un fichier texte
with open(os.path.join(FILENAME_OUTPUT), "w") as file:
    for description in df_cleaned["description"]:
        file.write(description + "\n")

    for description in summaries(df_cleaned):
        file.write(description + "\n")
