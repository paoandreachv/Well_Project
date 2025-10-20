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
    oriented_disc, manteo_lines = orient_disc_with_manteo(base_disc, azimuth, dip)

    # Transform disco
    trans = vtk.vtkTransform()
    trans.Translate(x, y, z)
    tdisc = vtk.vtkTransformPolyDataFilter()
    tdisc.SetTransform(trans)
    tdisc.SetInputData(oriented_disc)
    tdisc.Update()

    # Transform líneas
    trans2 = vtk.vtkTransform()
    trans2.Translate(x, y, z)
    tlines = vtk.vtkTransformPolyDataFilter()
    tlines.SetTransform(trans2)
    tlines.SetInputData(manteo_lines)
    tlines.Update()

    return tdisc.GetOutput(), tlines.GetOutput()

# TO TEST

def orient_disc_with_manteo(polydata, azimuth, dip, radius=50):
    """
    Rota el disco según Azimuth y Dip y crea:
      - oriented_disc: disco rotado
      - manteo_lines: línea del dip dentro del disco
    El dip cae 90° a la derecha del azimut (convención geológica).
    """

    # --- Rotar el disco ---
    transform = vtk.vtkTransform()
    transform.RotateZ(azimuth)   # azimut: dirección del rumbo
    transform.RotateX(dip)       # dip: inclinación desde la horizontal

    tf_filter = vtk.vtkTransformPolyDataFilter()
    tf_filter.SetTransform(transform)
    tf_filter.SetInputData(polydata)
    tf_filter.Update()
    oriented_disc = tf_filter.GetOutput()

    # --- Crear línea del dip (dentro del disco) ---
    pts = vtk.vtkPoints()
    lines = vtk.vtkCellArray()

    id0 = pts.InsertNextPoint(0.0, 0.0, 0.0)  # centro

    # Longitud de la línea: hasta el borde del disco
    length = radius * 0.9  # un poco menor al radio

    # La dirección del dip: 90° a la derecha del rumbo
    az_dip = -90 

    # Coordenadas del punto final dentro del disco (hacia abajo en Z)
    p1 = (length * np.sin(np.radians(az_dip)),
          length * np.cos(np.radians(az_dip)),
          -length * np.sin(np.radians(dip)))

    id1 = pts.InsertNextPoint(p1)

    line = vtk.vtkLine()
    line.GetPointIds().SetId(0, id0)
    line.GetPointIds().SetId(1, id1)
    lines.InsertNextCell(line)

    manteo_poly = vtk.vtkPolyData()
    manteo_poly.SetPoints(pts)
    manteo_poly.SetLines(lines)

    # Aplicar la misma rotación al manteo
    tf2 = vtk.vtkTransformPolyDataFilter()
    tf2.SetTransform(transform)
    tf2.SetInputData(manteo_poly)
    tf2.Update()
    manteo_transformed = tf2.GetOutput()

    return oriented_disc, manteo_transformed

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