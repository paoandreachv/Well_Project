import random, vtk, numpy as np

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
    """Orienta y traslada un disco y sus líneas de manteo."""
    oriented_disc, azimuth_poly, dip_transformed = orient_disc_with_manteo(base_disc, azimuth, dip)

    # Transform disco
    trans = vtk.vtkTransform()
    trans.Translate(x, y, z)
    tdisc = vtk.vtkTransformPolyDataFilter()
    tdisc.SetTransform(trans)
    tdisc.SetInputData(oriented_disc)
    tdisc.Update()

    # Transform lines
    trans2 = vtk.vtkTransform()
    trans2.Translate(x, y, z)
    tlines = vtk.vtkTransformPolyDataFilter()
    tlines.SetTransform(trans2)
    tlines.SetInputData(dip_transformed)
    tlines.Update()
    
    trans3 = vtk.vtkTransform()
    trans3.Translate(x, y, z)
    tlines_strike = vtk.vtkTransformPolyDataFilter()
    tlines_strike.SetTransform(trans3)
    tlines_strike.SetInputData(azimuth_poly)
    tlines_strike.Update()

    return tdisc.GetOutput(), tlines.GetOutput(), tlines_strike.GetOutput()

# TO TEST

def orient_disc_with_manteo(polydata, azimuth, dip, radius=50):
    """
    Rota el disco según Azimuth y Dip y crea:
      - oriented_disc: disco rotado
      - manteo_lines: línea del dip dentro del disco
    El dip cae 90° a la derecha del azimut (convención geológica).
    """

    # Rotar el disco
    transform = vtk.vtkTransform()
    transform.RotateZ(azimuth)   # azimut: dirección del rumbo
    transform.RotateX(dip)       # dip: inclinación desde la horizontal

    tf_filter = vtk.vtkTransformPolyDataFilter()
    tf_filter.SetTransform(transform)
    tf_filter.SetInputData(polydata)
    tf_filter.Update()
    oriented_disc = tf_filter.GetOutput()

    # Strike line
    # La línea del rumbo es horizontal (en la superficie del disco antes de rotar)
    pts_strike = vtk.vtkPoints()
    lines_strike = vtk.vtkCellArray()

    id0 = pts_strike.InsertNextPoint(-radius * 0.9, 0.0, 0.0)
    id1 = pts_strike.InsertNextPoint(radius * 0.9, 0.0, 0.0)

    line_strike = vtk.vtkLine()
    line_strike.GetPointIds().SetId(0, id0)
    line_strike.GetPointIds().SetId(1, id1)
    lines_strike.InsertNextCell(line_strike)

    azimuth_poly = vtk.vtkPolyData()
    azimuth_poly.SetPoints(pts_strike)
    azimuth_poly.SetLines(lines_strike)
    
    tf_strike = vtk.vtkTransformPolyDataFilter()
    tf_strike.SetTransform(transform)
    tf_strike.SetInputData(azimuth_poly)
    tf_strike.Update()
    azimuth_transformed = tf_strike.GetOutput()

    # Dip line
    # En el disco sin rotar, el manteo está perpendicular al rumbo (eje Y)
    pts_dip = vtk.vtkPoints()
    lines_dip = vtk.vtkCellArray()

    # En el plano XY del disco: Y perpendicular al strike
    id0d = pts_dip.InsertNextPoint(0.0, -radius*0.5, 0.0)
    id1d = pts_dip.InsertNextPoint(0.0, 0.0, 0.0)

    line_dip = vtk.vtkLine()
    line_dip.GetPointIds().SetId(0, id0d)
    line_dip.GetPointIds().SetId(1, id1d)
    lines_dip.InsertNextCell(line_dip)

    dip_poly = vtk.vtkPolyData()
    dip_poly.SetPoints(pts_dip)
    dip_poly.SetLines(lines_dip)

    # Aplicar la misma rotación a ambas líneas
    tf = vtk.vtkTransformPolyDataFilter()
    tf.SetTransform(transform)
    tf.SetInputData(dip_poly)
    tf.Update()
    dip_transformed = tf.GetOutput()

    return oriented_disc, azimuth_transformed, dip_transformed

# TESTED

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