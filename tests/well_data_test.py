# Asserts to verify well_data.py functionality
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import src.well_data as wd

# Test for well data
assert os.path.exists(wd.file_path), "The specified folder path does not exist"
assert not wd.load_well_data().empty

expected_columns = {"WellName",	"X", "Y", "Z", "MD", "MarkerName", "Dip", "Azimuth", "Point_number", "Marker_fault"}
assert expected_columns.issubset(wd.load_well_data().columns), "load_well_data() DataFrame does not contain expected column"

not_expected_columns = {"Depth", "Latitude", "Longitude"}
for data in not_expected_columns:
    assert data not in wd.load_well_data().columns, f"load_well_data() DataFrame should not contain column: {data}"

# Test for well trajectories
assert os.path.exists(wd.file_txt), "The specified folder path does not exist"
assert not wd.load_well_trajectories().empty

expected_columns1 = {"WELLNAME", "X", "Y", "Z", "MD"}
assert expected_columns1.issubset(wd.load_well_trajectories().columns), "load_well_trajectories() DataFrame does not contain expected column"

not_expected_columns1 = {"MarkerName", "Dip", "Azimuth", "Point_number", "Marker_fault"}
for data in not_expected_columns1:
    assert data not in wd.load_well_trajectories().columns, f"load_well_trajectories() DataFrame should not contain column: {data}"
    
# Test for edges 
assert not wd.edges == [], "Edges list should not be empty"
assert os.path.exists(wd.folder_path), "The specified folder path does not exist"
assert len(wd.csv_files) == 23, f"Expected 23 CSV files, found {len(wd.csv_files)}"

expected_columns2 = {"Seg_id", "X", "Y", "Z", "potential", "point"}
for edge_df, file in zip(wd.edges, wd.csv_files):
    assert expected_columns2.issubset(edge_df.columns), "An edge DataFrame does not contain expected column"
    with open(file, 'r') as f:
        total_lines = sum(1 for _ in f) -1
    assert len(edge_df) == total_lines, "An edge DataFrame does not have the expected number of rows"
        
    
    
