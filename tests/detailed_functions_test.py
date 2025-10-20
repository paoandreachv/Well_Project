import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import vtk, math
from src.detailed_functions import generate_distinct_colors, group_points_by_marker, create_actor
from src.vtk_objects import create_points
from src.well_data import load_well_data

well_data = load_well_data()
polydata, unique_markers = create_points(well_data)
n_colors = len(unique_markers)

grouped = group_points_by_marker(polydata, n_colors)

# Verify that the result is a dictionary with correct quantity of keys
assert isinstance(grouped, dict)
assert set(grouped.keys()) == set(range(n_colors))

# Each point should be a tuple of length 5 (x, y, z, azimuth, dip)
for key, points in grouped.items():
    for point in points:
        assert isinstance(point, tuple)
        assert len(point) == 5
        x, y, z, azimuth, dip = point
        # Each coordinate should be a float
        assert all(isinstance(coord, float) for coord in (x, y, z, azimuth, dip))

# Verify color table generation
color_table = generate_distinct_colors(n_colors)
assert isinstance(color_table, vtk.vtkLookupTable)
assert color_table.GetNumberOfTableValues() == n_colors

# Verify that each color is a tuple of 4 floats (RGBA)
for i in range(n_colors):
    rgba = color_table.GetTableValue(i)
    assert isinstance(rgba, tuple)
    assert len(rgba) == 4
    assert all(isinstance(component, float) for component in rgba)

# Verify create_actor function

lines = vtk.vtkCellArray()
line = vtk.vtkLine()
line.GetPointIds().SetId(0, 0)
line.GetPointIds().SetId(1, 0)
lines.InsertNextCell(line)

polydata_test = vtk.vtkPolyData()
polydata_test.SetLines(lines)

# Test 1: actor with color
color = (1.0, 0.0, 0.0)
actor1 = create_actor(polydata_test, color=color, line=False)

prop1 = actor1.GetProperty()
r, g, b = prop1.GetColor()

assert math.isclose(r, 1.0, abs_tol=1e-6)
assert math.isclose(g, 0.0, abs_tol=1e-6)
assert math.isclose(b, 0.0, abs_tol=1e-6)
assert math.isclose(prop1.GetOpacity(), 0.9, abs_tol=1e-6)
assert prop1.GetEdgeVisibility() == 0

# Test 2: line actor with line 
color2 = (0.0, 1.0, 0.0)
line_width = 3.0
actor2 = create_actor(polydata_test, color=color2, line=True, line_width=line_width)

prop2 = actor2.GetProperty()
r2, g2, b2 = prop2.GetColor()

assert math.isclose(r2, 0.0, abs_tol=1e-6)
assert math.isclose(g2, 1.0, abs_tol=1e-6)
assert math.isclose(b2, 0.0, abs_tol=1e-6)
assert math.isclose(prop2.GetLineWidth(), line_width, abs_tol=1e-6)
assert prop2.GetRepresentation() == vtk.VTK_WIREFRAME
assert prop2.GetLighting() == 0

# Test 3: actor without color
actor3 = create_actor(polydata_test)
prop3 = actor3.GetProperty()

r3, g3, b3 = prop3.GetColor()

assert math.isclose(r3, 1.0, abs_tol=1e-6)
assert math.isclose(g3, 1.0, abs_tol=1e-6)
assert math.isclose(b3, 1.0, abs_tol=1e-6)
