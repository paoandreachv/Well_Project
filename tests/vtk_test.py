import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np  
import vtk
from src.well_data import load_well_data, load_well_trajectories
from src.vtk_objects import create_points, create_well_line_actors
from vtk.util import numpy_support #type: ignore

well_data = load_well_data()
polydata, unique_markers = create_points(well_data)

# Test 1: Check polydata points
assert polydata.GetNumberOfPoints() == len(well_data), \
    f"Number of points in polydata '({polydata.GetNumberOfPoints()})' \
        does not match row numbers on well data '({len(well_data)})'."
        
# Test 2: Arrays existence and length
for array_name in ["Marker_fault", "Azimuth", "Dip"]:
    array = polydata.GetPointData().GetArray(array_name)
    assert array is not None, f"Array '{array_name}' not found in polydata point data."
    assert array.GetNumberOfTuples() == len(well_data), \
        f"Array '{array_name}' length ({array.GetNumberOfTuples()}) does not match row numbers on well data ({len(well_data)})."

# Test 3: Values matching
marker_ids = np.array([unique_markers[m] for m in well_data["MarkerName"]])
vtk_marker_ids = numpy_support.vtk_to_numpy(polydata.GetPointData().GetArray("Marker_fault"))
assert np.all(marker_ids == vtk_marker_ids), "Marker_fault values does not match"

# Azimuth
azimuth = well_data["Azimuth"].to_numpy(dtype=float)
vtk_azimuth = numpy_support.vtk_to_numpy(polydata.GetPointData().GetArray("Azimuth"))
assert np.allclose(azimuth, vtk_azimuth), "Azimuth values does not match"

# Dip
dip = well_data["Dip"].to_numpy(dtype=float)
vtk_dip = numpy_support.vtk_to_numpy(polydata.GetPointData().GetArray("Dip"))
assert np.allclose(dip, vtk_dip), "Dip values does not match"

well_trajectories = load_well_trajectories()
actors = create_well_line_actors(well_trajectories)

# Tests
for well in well_trajectories["WELLNAME"].unique():
    subset = well_trajectories[well_trajectories["WELLNAME"] == well].sort_values("Z", ascending=False)
    
    # Test 1: Verify that Z coordinates are in ascending order
    z = subset["Z"].to_numpy()
    assert np.all(z[:-1] >= z[1:]), f"Z coordinates for well '{well}' are not in ascending order."
    
    # Test 2: Verify that label positions are over the superficial points
    top_point = subset.iloc[0][["X", "Y", "Z"]].to_numpy()
    
    text_actors = [actor for actor in actors if isinstance(actor, vtk.vtkBillboardTextActor3D) and actor.GetInput() == well]
    assert len(text_actors) == 1, f"Expected one text actor for well '{well}', found {len(text_actors)}."
    
    position = np.array(text_actors[0].GetPosition())
    distance = np.linalg.norm(position - top_point)
    assert distance < 1e-3, f"Text actor for well '{well}' is not positioned over the top point."
    

