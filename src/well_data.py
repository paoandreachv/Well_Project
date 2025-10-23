import pandas as pd
import glob
import os


# Open a .csv file and a .txt file containing well data and well trajectories respectively
file_path = ("C:/Users/paope/Documents/Intercambio/Proyecto Octubre - Noviembre/"
             "WellVisualisationProject/WellVisualisationProject/Observations.csv")

file_txt = ("C:/Users/paope/Documents/Intercambio/Proyecto Octubre - Noviembre/"
             "WellVisualisationProject/WellVisualisationProject/Well_trajectories.txt")

def load_well_data():
    """ Loads well data from a .csv and returns a dataframe """
    return pd.read_csv(file_path)

def load_well_trajectories():
    """ Loads well trajectories data from a .txt and returns a dataframe """
    return pd.read_csv(file_txt, sep=r'\s+')

# Folder path for edge .csv files
folder_path = os.path.join("C:/Users/paope/Documents/Intercambio/Proyecto Octubre - Noviembre/",
                           "WellVisualisationProject/WellVisualisationProject/edges")

# Get all .csv files in the folder
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

# Read each file and store DataFrames in a list
edges = []
for file in csv_files:
    df = pd.read_csv(file)
    edges.append(df)

