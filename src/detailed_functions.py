import random, vtk, math

##################################################################
# -----------------------USEFUL FUNCTIONS----------------------- #
##################################################################

def normalize(v):
    x, y, z = v
    n = math.sqrt(x*x + y*y + z*z)
    return (x/n, y/n, z/n) if n != 0 else (0,0,0)

##################################################################
# ---------------------------COLORS----------------------------- #
##################################################################

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

##################################################################
# ---------------------------LINES------------------------------ #
##################################################################

def build_line(p0, p1):
    """ Return a vtkPolyData representing a single line from p0 to p1 """
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()
    id0 = points.InsertNextPoint(*p0) ### que hace el asterisco 
    id1 = points.InsertNextPoint(*p1) 
    line = vtk.vtkLine()
    line.GetPointIds().SetId(0, id0)
    line.GetPointIds().SetId(1, id1)
    lines.InsertNextCell(line)
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(lines)
    
    return polydata

def create_strike_dip_lines(radius=1.0):
    """ Create and return base strike and dip lines as vtkPolyData """
    epsilon = max(radius * 1e-3, 0.01)

    strike = build_line((-radius, 0.0, epsilon), (radius, 0.0, epsilon))
    dip = build_line((0.0, 0.0, epsilon), (0.0, radius, epsilon))

    return strike, dip

##################################################################
# ------------------------ORIENTATION--------------------------- #
##################################################################

def strike_vector(azimuth):
    """ Compute a horizontal strike vector from azimuth in degrees and return normalized vector"""
    azimuth_rad = math.radians(azimuth)
    strike_vec = normalize((math.sin(azimuth_rad), math.cos(azimuth_rad), 0.0))
    return strike_vec

def rotate_vector_about_z(v, angle_deg):
    """ Rotate a vector v about Z by angle_deg and return normalized rotated vector """
    az_transform = vtk.vtkTransform()
    az_transform.RotateZ(angle_deg)
    
    p = [v[0], v[1], v[2], 1.0]
    mat = az_transform.GetMatrix()
    rotated = [
        mat.GetElement(0,0)*p[0] + mat.GetElement(0,1)*p[1] + mat.GetElement(0,2)*p[2],
        mat.GetElement(1,0)*p[0] + mat.GetElement(1,1)*p[1] + mat.GetElement(1,2)*p[2],
        mat.GetElement(2,0)*p[0] + mat.GetElement(2,1)*p[1] + mat.GetElement(2,2)*p[2],
    ]
    return normalize(rotated)

def apply_transform(polydata, transform):
    """ Apply a vtkTransform to a vtkPolyData and return the transformed polydata """
    tf_filter = vtk.vtkTransformPolyDataFilter()
    tf_filter.SetTransform(transform)
    tf_filter.SetInputData(polydata)
    tf_filter.Update()
    transformed_polydata = tf_filter.GetOutput()
    
    return transformed_polydata
    

def orient_disc_with_manteo(polydata, azimuth, dip, radius=1):
    """ Orients a disc according to azimuth and dip values"""

    strike_vec = strike_vector(azimuth)
    rotated_strike = rotate_vector_about_z(strike_vec, azimuth)
    
    tf = vtk.vtkTransform()
    tf.RotateZ(azimuth)
    tf.RotateWXYZ(dip, rotated_strike[0], rotated_strike[1], rotated_strike[2])
    
    oriented_disc = apply_transform(polydata, tf)
    
    strike_base, dip_base = create_strike_dip_lines(radius)
    strike_oriented = apply_transform(strike_base, tf)
    dip_oriented = apply_transform(dip_base, tf)

    return oriented_disc, strike_oriented, dip_oriented

##################################################################
# --------------------TRANSFORM GEOMETRY------------------------ #
##################################################################

def translate(polydata, x, y, z):
    """ Returns a translated copy of the given polydata"""
    T = vtk.vtkTransform()
    T.Translate(x, y, z)
    return apply_transform(polydata, T)
    
def create_transformed_geometry(base_disc, x, y, z, azimuth, dip):
    """Moves a disc and its strike and dip lines based on coordinates"""
    oriented_disc, oriented_strike, oriented_dip = orient_disc_with_manteo(base_disc, azimuth, dip)

    disc_t = translate(oriented_disc, x, y, z)
    dip_t = translate(oriented_dip, x, y, z)
    strike_t = translate(oriented_strike, x, y, z)

    return disc_t, strike_t, dip_t

##################################################################
# ---------------------------ACTOR------------------------------ #
##################################################################

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
            actor.GetProperty().SetColor(color[:3])
        else:
            actor.GetProperty().SetOpacity(0.9)
            actor.GetProperty().EdgeVisibilityOff()
    
    return actor