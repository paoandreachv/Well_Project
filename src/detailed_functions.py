import random, vtk, math

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

def create_transformed_geometry(base_disc, x, y, z, azimuth, dip):
    """Moves a disc and its strike and dip lines based on coordinates"""
    oriented_disc, azimuth_poly, dip_transformed = orient_disc_with_manteo(base_disc, azimuth, dip)

    # Transform disc
    trans = vtk.vtkTransform()
    trans.Translate(x, y, z)
    tdisc = vtk.vtkTransformPolyDataFilter()
    tdisc.SetTransform(trans)
    tdisc.SetInputData(oriented_disc)
    tdisc.Update()

    # Transform lines
    tlines = vtk.vtkTransformPolyDataFilter()
    tlines.SetTransform(trans)
    tlines.SetInputData(dip_transformed)
    tlines.Update()
    
    tlines_strike = vtk.vtkTransformPolyDataFilter()
    tlines_strike.SetTransform(trans)
    tlines_strike.SetInputData(azimuth_poly)
    tlines_strike.Update()

    return tdisc.GetOutput(), tlines.GetOutput(), tlines_strike.GetOutput()

def normalize(v):
    x, y, z = v
    n = math.sqrt(x*x + y*y + z*z)
    return (x/n, y/n, z/n) if n != 0 else (0,0,0)

def orient_disc_with_manteo(polydata, azimuth, dip, radius=1):
    """ Orients a disc according to azimuth and dip values"""
        
    # Orients the disc
    azimuth_rad = math.radians(azimuth)
    strike_vec = (math.sin(azimuth_rad), math.cos(azimuth_rad), 0)
    strike_vec = normalize(strike_vec)
    
    az_transform = vtk.vtkTransform()
    az_transform.RotateZ(azimuth)
    
    p = [strike_vec[0], strike_vec[1], strike_vec[2], 1.0]
    mat = az_transform.GetMatrix()
    rotated_strike = [
        mat.GetElement(0,0)*p[0] + mat.GetElement(0,1)*p[1] + mat.GetElement(0,2)*p[2],
        mat.GetElement(1,0)*p[0] + mat.GetElement(1,1)*p[1] + mat.GetElement(1,2)*p[2],
        mat.GetElement(2,0)*p[0] + mat.GetElement(2,1)*p[1] + mat.GetElement(2,2)*p[2],
    ]
    rotated_strike = normalize(rotated_strike)
    
    transform = vtk.vtkTransform()
    transform.RotateZ(azimuth)
    transform.RotateWXYZ(dip, *rotated_strike)   

    tf_filter = vtk.vtkTransformPolyDataFilter()
    tf_filter.SetTransform(transform)
    tf_filter.SetInputData(polydata)
    tf_filter.Update()
    oriented_disc = tf_filter.GetOutput()

    # Lines
    strike_line, dip_line = create_strike_dip_lines(radius)
    
    tf_strike = vtk.vtkTransformPolyDataFilter()
    tf_strike.SetTransform(transform)
    tf_strike.SetInputData(strike_line)
    tf_strike.Update()
    azimuth_transformed = tf_strike.GetOutput()
    
    tf_dip = vtk.vtkTransformPolyDataFilter()
    tf_dip.SetTransform(transform)
    tf_dip.SetInputData(dip_line)
    tf_dip.Update()
    dip_transformed = tf_dip.GetOutput()

    return oriented_disc, azimuth_transformed, dip_transformed

def create_strike_dip_lines(radius=1.0):
    """Crea las líneas base (strike y dip)."""
    # Strike line (X axis)
    pts_strike = vtk.vtkPoints()
    lines_strike = vtk.vtkCellArray()
    id0 = pts_strike.InsertNextPoint(-radius, 0.0, 0.0)
    id1 = pts_strike.InsertNextPoint(radius, 0.0, 0.0)
    line_strike = vtk.vtkLine()
    line_strike.GetPointIds().SetId(0, id0)
    line_strike.GetPointIds().SetId(1, id1)
    lines_strike.InsertNextCell(line_strike)
    azimuth_poly = vtk.vtkPolyData()
    azimuth_poly.SetPoints(pts_strike)
    azimuth_poly.SetLines(lines_strike)

    # Dip line (Y axis)
    pts_dip = vtk.vtkPoints()
    lines_dip = vtk.vtkCellArray()
    id0d = pts_dip.InsertNextPoint(0.0, 0.0, 0.0)
    id1d = pts_dip.InsertNextPoint(0.0, radius, 0.0)
    line_dip = vtk.vtkLine()
    line_dip.GetPointIds().SetId(0, id0d)
    line_dip.GetPointIds().SetId(1, id1d)
    lines_dip.InsertNextCell(line_dip)
    dip_poly = vtk.vtkPolyData()
    dip_poly.SetPoints(pts_dip)
    dip_poly.SetLines(lines_dip)

    return azimuth_poly, dip_poly


def create_actor(polydata, color = None, line = False, line_width = 2.0):
    """ Create a VTK actor from polydata, configuring its color and style"""
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    if color is not None:
        actor.GetProperty().SetColor(color[:3])
        if line:
            actor.GetProperty().SetLineWidth(line_width)
            actor.GetProperty().SetRepresentationToWireframe()
            actor.GetProperty().LightingOff()
        else:
            actor.GetProperty().SetOpacity(0.9)
            actor.GetProperty().EdgeVisibilityOff()
    
    return actor