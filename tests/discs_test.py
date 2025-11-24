import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import vtk
import numpy as np
from src.geometry import orient_disc_with_manteo, create_transformed_geometry
from src.well_data import load_well_data

data = load_well_data()

wellname = "NE6"
wellname1 = "NS23"
subset = data[data["WellName"] == wellname].copy()
subset1 = data[data["WellName"] == wellname1].copy()

# Test 1: Well existence
assert not subset.empty, f"Well '{wellname}' does not exist in the data"
assert subset1.empty, f"Well '{wellname1}' does not exist in the data"

# Tests 
azimuth = subset["Azimuth"].iloc[0]
dip = subset["Dip"].iloc[0]
x, y, z = subset[["X", "Y", "Z"]].iloc[0]

# Create a base disc
disc = vtk.vtkDiskSource()
disc.SetInnerRadius(0.0)
disc.SetOuterRadius(50.0)
disc.SetRadialResolution(1)
disc.SetCircumferentialResolution(10)
disc.Update()
polydata = disc.GetOutput()

oriented_disc, strike_line, dip_line = orient_disc_with_manteo(
    polydata, azimuth, dip, radius=50
)

# Test 2: Check outputs are valid
assert isinstance(oriented_disc, vtk.vtkPolyData)
assert isinstance(strike_line, vtk.vtkPolyData)
assert isinstance(dip_line, vtk.vtkPolyData)

# Test 3: Verifies that dip line is inclined according to dip angle
p0 = np.array(dip_line.GetPoint(0))
p1 = np.array(dip_line.GetPoint(1))
dip_vector = p1 - p0
dip_angle_calc= np.degrees(np.arctan2(-dip_vector[2], np.linalg.norm(dip_vector[:2])))

assert np.isclose(dip_angle_calc, dip, atol=5.0), \
    f"Dip line angle ({dip_angle_calc:.2f}°) does not match expected dip ({dip}°)"
    
# Test 4: Verifies that strike line is coherent
p0az = np.array(strike_line.GetPoint(0))
p1az = np.array(strike_line.GetPoint(1))
strike_vector = p1az - p0az
azimuth_calc = (np.degrees(np.arctan2(strike_vector[1], strike_vector[0])) + 360) % 360

assert np.isclose(azimuth_calc, azimuth, atol=5.0), \
    f"Strike line azimuth ({azimuth_calc:.2f}°) does not match expected azimuth ({azimuth}°)"
    

