
##################################################################
# ------------------------GROUP POINTS-------------------------- #
##################################################################
def read_points(polydata):
    """ Read points and their attributes from vtkPolyData """
    marker = polydata.GetPointData().GetArray("Marker_fault")
    az = polydata.GetPointData().GetArray("Azimuth")
    dp = polydata.GetPointData().GetArray("Dip")
    return marker, az, dp

def group_points_by_marker(polydata, n_colors):
    """ Group the polydata points by marker_fault """
    marker_array, azimuth_array, dip_array = read_points(polydata)
    marker_to_points = {i: [] for i in range(n_colors)}
    for i in range(polydata.GetNumberOfPoints()):
        m = int(marker_array.GetTuple1(i))
        x, y, z = polydata.GetPoint(i)
        azimuth = azimuth_array.GetValue(i)
        dip = dip_array.GetValue(i)
        marker_to_points[m].append((x, y, z, azimuth, dip))
    return marker_to_points