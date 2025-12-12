import vtk
import src.geometry as geometry
import src.colors as colors
import src.group_points as group_points
import src.actors as actors
from vtk.util import numpy_support #type: ignore

##################################################################
# -----------------------DATA EXTRACTION------------------------ #
##################################################################

def extract_numpy_arrays(well_data):
    """ Extract numpy arrays for coords, markers, azimuth and dip """
    coords = well_data[["X", "Y", "Z"]].to_numpy(dtype=float)
    
    unique_markers = {name: i for i, name in enumerate(sorted(well_data["MarkerName"].unique()))}
    marker_ids = well_data["MarkerName"].map(unique_markers).to_numpy(dtype=int)
    
    azimuth = well_data["Azimuth"].to_numpy(dtype=float)
    dip = well_data["Dip"].to_numpy(dtype=float)
    return coords, marker_ids, azimuth, dip, unique_markers

def convert_to_vtk_arrays(coords, marker_ids, azimuth, dip):
    """ Convert numpy arrays into named VTK arrays """
    vtk_coords = numpy_support.numpy_to_vtk(coords)
    marker_fault_array = numpy_support.numpy_to_vtk(marker_ids)
    azimiuth_array = numpy_support.numpy_to_vtk(azimuth)
    dip_array = numpy_support.numpy_to_vtk(dip)

    # Assign a name to the array within VTK
    marker_fault_array.SetName("Marker_fault") 
    azimiuth_array.SetName("Azimuth")
    dip_array.SetName("Dip")
    return vtk_coords, marker_fault_array, azimiuth_array, dip_array

def build_points_polydata(vtk_coords, marker_fault_array, azimiuth_array, dip_array):
    """ Build a vtkPolyData object with points and attribute arrays"""
    points = vtk.vtkPoints()
    points.SetData(vtk_coords)
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    
    # Associate the set of values with the points I already have in polydata
    pd = polydata.GetPointData()
    pd.AddArray(marker_fault_array)
    pd.AddArray(azimiuth_array)
    pd.AddArray(dip_array)
    
    # Indicate which array will be used as the active array (for coloring)
    pd.SetActiveScalars("Marker_fault")
    return polydata

def create_points(well_data):
    """ Function that extracts data, converts arrays to VTK and builds the polydata object """
    coords, marker_ids, azimuth, dip, unique_markers = extract_numpy_arrays(well_data)
    vtk_coords, marker_fault_array, azimiuth_array, dip_array = convert_to_vtk_arrays(coords, marker_ids, azimuth, dip)
    polydata = build_points_polydata(vtk_coords, marker_fault_array, azimiuth_array, dip_array)
    return polydata, unique_markers

##################################################################
# -----------------------DISC GEOMETRY-------------------------- #
##################################################################

def prepare_disc_template(radius, resolution):
    """ Create and return the base disc geomtery used for all wells"""
    base_disc = vtk.vtkRegularPolygonSource()
    base_disc.SetCenter(0.0, 0.0, 0.0)
    base_disc.SetRadius(radius)
    base_disc.SetNumberOfSides(resolution)
    base_disc.Update()
    base_disc_output = base_disc.GetOutput()
    return base_disc_output

def build_marker_geometries(points, base_disc, transformed_fn):
    """ Create combined disc geometry and a list of line polydata for all points of a given marker.
        Returns: (append_discs_polydata, list_of_line_polydata)
    """
    append_discs = vtk.vtkAppendPolyData()
    line_polydatas = []  # collect each line polydata (strike and dip as separate entries)

    for (x, y, z, azimuth, dip) in points:
        disc_geom, strike_geom, dip_geom = transformed_fn(base_disc, x, y, z, azimuth, dip)
        append_discs.AddInputData(disc_geom)
        # collect the strike and dip separate polydata objects (already translated by transformed_fn)
        line_polydatas.append(strike_geom)
        line_polydatas.append(dip_geom)

    append_discs.Update()
    discs_out = append_discs.GetOutput()
    return discs_out, line_polydatas
    

def create_disc_line_actors(polydata, unique_markers, radius=200, resolution=40,
                               line_color=(0, 0, 0), line_width=2.0):
    """ Build actors for discs and lines """
    n_colors = len(unique_markers)
    color_table = colors.generate_distinct_colors(n_colors)
    marker_to_points = group_points.group_points_by_marker(polydata, n_colors)

    base_disc = prepare_disc_template(radius, resolution)
    actors_ = []

    for marker_index, points in marker_to_points.items():
        if not points:
            continue

        disc_geom, line_polydatas = build_marker_geometries(points, base_disc, geometry.create_transformed_geometry)

        # Disc actor
        disc_color = color_table.GetTableValue(marker_index)
        disc_actor = actors.create_actor(disc_geom, color=disc_color, line=False)
        actors_.append(disc_actor)

        # Create separate actors for each line polydata (strike and dip)
        for line_pd in line_polydatas:
            # create tube-based line actor for visibility
            line_actor = actors.create_actor(line_pd, color=line_color, line=True, line_width=line_width)
            actors_.append(line_actor)
    return actors_

##################################################################
# -------------------------WELL LINES--------------------------- #
##################################################################

def build_well_polyline(subset):
    """ Create vtkPolyData for the well trajectory """
    points = vtk.vtkPoints()
    for _, row in subset.iterrows():
        points.InsertNextPoint(row["X"], row["Y"], row["Z"])
        
    lines = vtk.vtkCellArray()
    for i in range(len(subset) - 1):
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, i)
        line.GetPointIds().SetId(1, i + 1)
        lines.InsertNextCell(line)
        
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(lines)
    return polydata
    

