# Asserts to verify well_data.py functionality
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import src.well_data as wd

# Verify that DataFrames are not empty and contain expected columns
assert not wd.load_well_data().empty

expected_columns = {"WellName",	"X", "Y", "Z", "MD", "MarkerName", "Dip", "Azimuth", "Point_number", "Marker_fault"}
assert expected_columns.issubset(wd.load_well_data().columns), "load_well_data() DataFrame does not contain expected column"

not_expected_columns = {"Depth", "Latitude", "Longitude"}
for data in not_expected_columns:
    assert data not in wd.load_well_data().columns, f"load_well_data() DataFrame should not contain column: {data}"



assert not wd.load_well_trajectories().empty

expected_columns1 = {"WELLNAME", "X", "Y", "Z", "MD"}
assert expected_columns1.issubset(wd.load_well_trajectories().columns), "load_well_trajectories() DataFrame does not contain expected column"

not_expected_columns1 = {"MarkerName", "Dip", "Azimuth", "Point_number", "Marker_fault"}
for data in not_expected_columns1:
    assert data not in wd.load_well_trajectories().columns, f"load_well_trajectories() DataFrame should not contain column: {data}"