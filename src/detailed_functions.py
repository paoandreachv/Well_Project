import random, vtk


def generate_distinct_colors(n_colors):
    """ Build a random color table for each marker """
    # Creates a color table to assign a color to each marker
    table = vtk.vtkLookupTable()
    table.SetNumberOfTableValues(n_colors)
    table.Build()
    # The colors will be the same each time the code is run
    random.seed(0)  
    
    for i in range(n_colors):
        table.SetTableValue(i, random.random(), random.random(), random.random(), 1.0)
    return table


def group_points_by_marker(polydata, n_colors):
    """ Group the polydata points by marker_fault """
    marker_array = polydata.GetPointData().GetArray("Marker_fault")
    azimuth_array = polydata.GetPointData().GetArray("Azimuth")
    dip_array = polydata.GetPointData().GetArray("Dip")
    
    # Create a dictionary to hold points for each marker
    marker_to_points = {i: [] for i in range(n_colors)}
        
    for i in range(polydata.GetNumberOfPoints()):
        # Read the marker number that corresponds to each point
        m = int(marker_array.GetTuple1(i))
        x, y, z = polydata.GetPoint(i)
        azimuth = azimuth_array.GetValue(i)
        dip = dip_array.GetValue(i)
        marker_to_points[m].append((x, y, z, azimuth, dip)) 
    return marker_to_points