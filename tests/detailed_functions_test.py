import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import vtk, math
from src.detailed_functions import generate_distinct_colors, group_points_by_marker, create_actor, read_points, build_line, create_strike_dip_lines, strike_vector
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

###################################################################
# ----------------generate_distinct_colors----------------------- #
###################################################################

ct = generate_distinct_colors(5)
assert isinstance(ct, vtk.vtkLookupTable)
assert ct.GetNumberOfTableValues() == 5

###################################################################
# ----------------sintetic data for testing---------------------- #
###################################################################

poly = vtk.vtkPolyData()
pts = vtk.vtkPoints()
marker_arr = vtk.vtkIntArray(); marker_arr.SetName("Marker_fault")
az_arr = vtk.vtkFloatArray(); az_arr.SetName("Azimuth")
dp_arr = vtk.vtkFloatArray(); dp_arr.SetName("Dip")


for i in range(5):
    pts.InsertNextPoint(-i, i*2, i)
    marker_arr.InsertNextValue(i % 2)
    az_arr.InsertNextValue(float(i*10))
    dp_arr.InsertNextValue(float(i*5))


poly.SetPoints(pts)
poly.GetPointData().AddArray(marker_arr)
poly.GetPointData().AddArray(az_arr)
poly.GetPointData().AddArray(dp_arr)

###################################################################
# ------------------------read points---------------------------- #
###################################################################

m, a, d = read_points(poly)
assert m.GetNumberOfValues() == 5
assert a.GetNumberOfValues() == 5
assert d.GetNumberOfValues() == 5

###################################################################
# ----------------group points by marker----------------------- #
###################################################################

g = group_points_by_marker(poly, 2)
assert set(g.keys()) == {0,1}
for k,v in g.items():
    for tup in v:
        assert len(tup) == 5
        assert all(isinstance(t, float) for t in tup)
        
###################################################################
# -------------------------build line---------------------------- #
###################################################################

line_poly = build_line((0,0,0), (1,1,1))
assert isinstance(line_poly, vtk.vtkPolyData)
assert line_poly.GetNumberOfPoints() == 2

###################################################################
# -------------------create strike dip lines--------------------- #
###################################################################

s,d = create_strike_dip_lines(2)
assert s.GetNumberOfPoints() == 2
assert d.GetNumberOfPoints() == 2

###################################################################
# ------------------------strike vector-------------------------- #
###################################################################

sv = strike_vector(30)
assert len(sv) == 3
assert math.isclose(math.sqrt(sv[0]**2 + sv[1]**2 + sv[2]**2), 1, rel_tol=1e-6)

###################################################################
# -------------------rotate vector about z----------------------- #
###################################################################
from src.detailed_functions import rotate_vector_about_z, apply_transform, orient_disc_with_manteo, translate, normalize

rv = rotate_vector_about_z((1,0,0), 90)
assert rv == (0.0, 1.0, 0.0)
assert isinstance(rv, tuple)

###################################################################
# ---------------------apply transform--------------------------- #
###################################################################

T = vtk.vtkTransform(); T.Translate(1,2,3)
poly2 = apply_transform(line_poly, T)
assert poly2.GetPoint(0)[0] == line_poly.GetPoint(0)[0] + 1

###################################################################
# --------------------orient disc with manteo-------------------- #
###################################################################

disc = vtk.vtkDiskSource(); disc.Update()
disc_pd = disc.GetOutput()
translated = translate(disc_pd, 5,5,5)
print(translated.GetPoints())
assert isinstance(translated, vtk.vtkPolyData)

