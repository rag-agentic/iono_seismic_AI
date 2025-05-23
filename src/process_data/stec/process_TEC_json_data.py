import json
from collections import defaultdict
import pandas as pd
import glob
import os
import re
import csv
from datetime import datetime
import sys
import time

FILENAME_INPUT = "../../../raw_data/seismics/seismics_egee_30_10_2020.json"

FOLDER_INPUT = "../../../raw_data/TEC/gpl_06_02_2023"
FOLDER_OUTPUT = "../../../documents_to_RAG/"
STEC_THRESHOLD = 0.07


# extract data by hour
def extract_hourly_data(row):
    hourly_data = []
    for entry in row["data"]:
        timestamp = entry["time"]
        stec = entry["stec"]

        # Convert timestamp to hour
        hour = datetime.utcfromtimestamp(timestamp).hour
        hourly_data.append((hour, stec))

    return hourly_data


def format_value(value, threshold_min=0.5, threshold_max=5):
    # If value near threshold_min, return None
    if abs(value) > threshold_max:
        return f" is higher that normal, it's not current, his value is {value:.1f} , ionosphere can have perturbation"
    elif abs(value) < threshold_min:
        return None
    else:
        return f"{value:.1f}"


def classify_normalized_stec(value):
    if abs(value) < 0.2:
        return None
    elif abs(value) > 0.3 and abs(value) < 0.4:
        return "light disturbances"
    elif abs(value) > 0.4 and abs(value) < 0.45:
        return "moderate disturbances"
    elif abs(value) > 0.45 and abs(value) < 0.50:
        return "strong disturbances"
    elif abs(value) > 0.50 and abs(value) < 0.100:
        return "extreme disturbances"
        # Fonction de standardisation


def standardize(x):
    return (x - x.mean()) / x.std()


def statistics_TEC_data(filename, station_name, freq_value=False):
    hourly_data = []
    summaries = []
    list_sat = []
    is_data_present = False
    text = []
    activelink = 0

    with open(filename, "r") as file:
        data = json.load(file)

    # Parse data
    df = pd.DataFrame(data)
    print(df)
    activelink = df["activeLink"].iloc[0].astype(int)
    print(type(activelink))

    if not df.empty and activelink == 0:
        for idx, row in df.iterrows():
            hourly_data = []
            satellite_name = row["sat"]
            print(row)
            print(satellite_name)
            if satellite_name == "R859":
                time.sleep(5)
            list_sat.append(satellite_name)

            first_datetime = pd.to_datetime(row["data"][0]["time"], unit="s", utc=True)
            print(first_datetime)

            # first_date = pd.to_datetime(row['data']['time'], unit='s')
            for entry in row["data"]:
                # flattened_data.append({'sat': row['sat'], 'time': entry['time'], 'stec': entry['stec']})
                timestamp = entry["time"]
                stec = entry["stec"]
                datetime_val = pd.to_datetime(timestamp, unit="s")

                # Convertir le timestamp en heure
                hour = datetime.utcfromtimestamp(timestamp).hour
                hourly_data.append({"hour": hour, "stec": stec})

            hourly_df = pd.DataFrame(hourly_data)
            print(hourly_df)
            # Mean compute
            hourly_stats = (
                hourly_df.groupby("hour")["stec"]
                .agg(["mean", "std", "min", "max"])
                .reset_index()
            )
            # Merge stats
            # hourly_stats = hourly_stats.merge(hourly_stats, on='hour', how='left')

            # Normalization for each line
            # hourly_df['stec_normalized'] = (hourly_df['stec'] - hourly_df['min']) / (hourly_df['max']-hourly_df['min'])
            # hourly_df['stec_normalized'] = hourly_df['stec']
            # hourly_df['stec_normalized'] = (hourly_df['stec'] - hourly_df['mean']) / (hourly_df['std'])

            # Display hour with'hour' et 'stec_normalized'
            # hourly_df_standardized = hourly_stats[['hour', 'stec','max']]

            # Calculer les statistiques par heure
            """hourly_summary = hourly_df_standardized.groupby('hour').agg(
                mean=('stec_normalized', 'mean'),
                std=('stec_normalized', 'std'),
            ).reset_index()"""

            # Filtrer les lignes où 'std' > 0.3 dans le DataFrame agrégé
            # df_summary = hourly_summary[hourly_summary['std'] > 0.3]
            df_summary = hourly_stats
            print(df_summary)

            if not df_summary.empty:
                print(df_summary)
                for index, row in df_summary.iterrows():
                    hour = row["hour"]
                    mean = row["mean"]
                    std = row["std"]
                    max = row["max"]
                    # max_value = row['max']
                    # min_value = row['min']

                    str_classify_value = classify_normalized_stec(mean)
                    if str_classify_value is not None:
                        is_data_present = True
                        first_date = first_datetime.strftime("%Y-%m-%d")
                        # Text format
                        time_str = f"{hour}h"
                        # Building text
                        text = f"\nThe radio link from the satellite named {satellite_name} to the ground \
                        station {station_name}, at {first_date} from {time_str} to {hour+1}h is {str_classify_value} (stec={round(max,2)}) ."

                        """if mean_str is not None:  # Afficher la moyenne uniquement si elle n'est pas proche de 0
                            text += f" the mean value of STEC is {mean_str},"
                        if std_str is not None:  # Afficher l'écart type uniquement si il n'est pas proche de 0
                            text += f" the standard deviation value of STEC is {std_str},"
                        if max_str is not None:  # Afficher le max uniquement si il n'est pas proche de 0
                            text += f" the maximum STEC is {max_str},"
                        if min_str is not None:  # Afficher le min uniquement si il n'est pas proche de 0
                            text += f" and the minimum STEC is {min_str}."""

                        summaries.append(text)
                        print(summaries)
            else:
                text = f"For the satellite named {satellite_name}, at {first_datetime} no significant value of STEC is present"
            """if is_data_present is True:
                # Afficher ou enregistrer le texte
                summary = [f"Theses STEC (Slant Total Electron Content) measurements were collected \
                with the ground station {station_name} with satellite {list_sat}.\n"]
            else:
                summary = [ ]"""
        # print([item for item in summaries])
        # return summary+summaries
        return summaries
    else:
        return ""


def process_TEC_data(list_files, output_filename):

    data_text = []

    if os.path.exists(output_filename):
        os.remove(output_filename)
        print(f"Le fichier {output_filename} a été supprimé avec succès.")
    else:
        print(f"Le fichier {output_filename} n'existe pas.")

    header = "Theses STEC (Slant Total Electron Content) measurements were collected with the GPS ground station"
    with open(output_filename, "w") as file:
        file.write(header)

    print("Fichiers JSON trouvés commençant par 'TEC':")
    for fichier in list_files:
        print(os.path.basename(fichier))
        data_text = []

        # Extract base station
        pattern = r"TEC_measures_([A-Z0-9]+)\.json"
        pattern = r"_(\w{4})\.json$"
        match = re.search(pattern, fichier)
        station_name = match.group(1)

        print(fichier)
        data_text.append(statistics_TEC_data(fichier, station_name))

        with open(output_filename, "a") as file:
            for item in data_text:
                for item1 in item:
                    print(item1)
                    file.write(item1)


if __name__ == "__main__":

    # Find file starting by TEC
    TEC_list_file = glob.glob(os.path.join(FOLDER_INPUT, "TEC*.json"))
    print(TEC_list_file)
    output_filename = os.path.join(FOLDER_OUTPUT_TXT, f"summaries_TEC.txt")

    process_TEC_data(TEC_list_file, output_filename)
