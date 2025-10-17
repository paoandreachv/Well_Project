"""
well_data.py
"""

import pandas as pd
import glob
import os
import vtk


# Open a .csv file

file_path = ("C:/Users/paope/Documents/Intercambio/Proyecto Octubre - Noviembre/"
             "WellVisualisationProject/WellVisualisationProject/Observations.csv")

well_info = pd.read_csv(file_path)

# Folder path
folder_path = os.path.join("C:/Users/paope/Documents/Intercambio/Proyecto Octubre - Noviembre/",
                           "WellVisualisationProject/WellVisualisationProject/edges")

# Get all .csv files
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

# Read each file into a DataFrame
edges = []
for file in csv_files:
    df = pd.read_csv(file)
    edges.append(df)
    
print(edges)
    

