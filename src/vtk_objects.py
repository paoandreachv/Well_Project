import vtk, random, detailed_functions, numpy as np

def create_points(well_data):
    """ Creates VTK points from well coordinates """
    coords = well_data[["X", "Y", "Z"]].to_numpy(dtype=float)
    
    unique_markers = {name: i for i, name in enumerate(sorted(well_data["MarkerName"].unique()))}
    marker_ids = well_data["MarkerName"].map(unique_markers).to_numpy(dtype=int)
    
    azimuth = well_data["Azimuth"].to_numpy(dtype=float)
    dip = well_data["Dip"].to_numpy(dtype=float)
    
    points = vtk.vtkPoints()
    # Convert a numpy array into a VTK array
    points.SetData(vtk.util.numpy_support.numpy_to_vtk(coords))
    
    marker_fault_array = vtk.util.numpy_support.numpy_to_vtk(marker_ids)
    # Assign a name to the array within VTK
    marker_fault_array.SetName("Marker_fault")
    
    azimiuth_array = vtk.util.numpy_support.numpy_to_vtk(azimuth)
    azimiuth_array.SetName("Azimuth")
    
    dip_array = vtk.util.numpy_support.numpy_to_vtk(dip)
    dip_array.SetName("Dip")
    
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    # Associate the set of values with the points I already have in polydata
    polydata.GetPointData().AddArray(marker_fault_array)
    polydata.GetPointData().AddArray(azimiuth_array)
    polydata.GetPointData().AddArray(dip_array)
    # Indicate which array will be used as the active array (for coloring)
    polydata.GetPointData().SetActiveScalars("Marker_fault")
    
    return polydata, unique_markers

def create_filledpolygon_actor(polydata, unique_markers, radius = 100, resolution = 40,
                               line_color = (0, 0, 0), line_width = 2):
    n_colors = len(unique_markers)
    color_table = detailed_functions.generate_distinct_colors(n_colors)
    marker_to_points = detailed_functions.group_points_by_marker(polydata, n_colors)
    actors = []
    
    base_disc = vtk.vtkRegularPolygonSource()
    base_disc.SetCenter(0.0, 0.0, 0.0)
    base_disc.SetRadius(radius)
    base_disc.SetNumberOfSides(resolution)
    base_disc.Update()
    base_disc_output = base_disc.GetOutput()
