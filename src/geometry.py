import vtk, math

##################################################################
# -----------------------USEFUL FUNCTIONS----------------------- #
##################################################################
def normalize(v):
    x, y, z = v
    n = math.sqrt(x*x + y*y + z*z)
    return (x/n, y/n, z/n) if n != 0 else (0.0, 0.0, 0.0)

def dot(a, b):
    """ Compute the dot product of two 3D vectors """
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def cross(a, b):
    """ Compute the cross product of two 3D vectors """
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])

##################################################################
# ---------------------------LINES------------------------------ #
##################################################################
def build_line(p0, p1):
    """ Return a vtkPolyData representing a single line from p0 to p1 """
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()
    id0 = points.InsertNextPoint(*p0)
    id1 = points.InsertNextPoint(*p1)
    line = vtk.vtkLine()
    line.GetPointIds().SetId(0, id0)
    line.GetPointIds().SetId(1, id1)
    lines.InsertNextCell(line)
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(lines)
    return polydata

##################################################################
# ------------------------ORIENTATION--------------------------- #
##################################################################

def _transform_from_normals(n_from=(0,0,1), n_to=(0,0,1)):
    """
    Return vtkTransform that rotates n_from into n_to using axis=cross and angle=acos(dot).
    Handles parallel and antiparallel cases.
    """
    n1 = normalize(n_from)
    n2 = normalize(n_to)
    dp = dot(n1, n2)
    dp = max(-1.0, min(1.0, dp))
    angle_rad = math.acos(dp)
    angle_deg = math.degrees(angle_rad)
    tf = vtk.vtkTransform()
    # no rotation needed
    if abs(angle_deg) < 1e-8:
        return tf
    # antiparallel case: rotate 180 about an orthogonal axis
    if abs(abs(dp) - 1.0) < 1e-9 and dp < 0:
        # pick an orthogonal axis
        candidate = cross(n1, (1.0, 0.0, 0.0))
        if math.isclose(math.sqrt(dot(candidate, candidate)), 0.0, rel_tol=1e-9, abs_tol=1e-12):
            candidate = cross(n1, (0.0, 1.0, 0.0))
        ax = normalize(candidate)
        tf.RotateWXYZ(180.0, ax[0], ax[1], ax[2])
        return tf
    axis = cross(n1, n2)
    axis = normalize(axis)
    tf.RotateWXYZ(angle_deg, axis[0], axis[1], axis[2])
    return tf

def apply_transform(polydata, transform):
    """ Apply a vtkTransform to a vtkPolyData and return the transformed polydata """
    tf_filter = vtk.vtkTransformPolyDataFilter()
    tf_filter.SetTransform(transform)
    tf_filter.SetInputData(polydata)
    tf_filter.Update()
    transformed_polydata = tf_filter.GetOutput()
    return transformed_polydata

def compute_plane_normal(azimuth_deg, dip_deg):
    """ Compute the normal vector of a plane given azimuth and dip angles"""
    # 2) Normal del plano
    az = math.radians(azimuth_deg)
    d  = math.radians(dip_deg)

    # normal pointing up
    nx = math.sin(az) * math.sin(d)
    ny = math.cos(az) * math.sin(d)
    nz = math.cos(d)
    return normalize((nx, ny, nz))

def compute_local_axes(dip_dir_deg, dip_deg, normal):
    """ Build local exes """
    # e3 = normal
    e3 = normal

    # Strike = dip direction - 90
    strike_angle = math.radians((dip_dir_deg - 90) % 360)
    strike_vec = (math.sin(strike_angle), math.cos(strike_angle), 0.0)

    # e1 = strike (horizontal)
    e1 = normalize(strike_vec)

    # e2 = dip direction (horizontal)
    az = math.radians(dip_dir_deg)
    d = math.radians(dip_deg)
    dip_vec = (math.sin(az), math.cos(az), -math.sin(d))
    e2 = normalize(dip_vec)
    return e1, e2, e3
    
    
def compute_line_endpoints(radius):
    azimuth = (( -radius/1.5, 0, 0 ), (  radius/1.5, 0, 0 ))
    dip = ((0,0,0), (0, radius/1.5, 0))
    return azimuth, dip

def local_to_global(e1, e2, e3, local_point):
    x, y, z = local_point
    gx = x*e1[0] + y*e2[0] + z*e3[0]
    gy = x*e1[1] + y*e2[1] + z*e3[1]
    gz = x*e1[2] + y*e2[2] + z*e3[2]
    return (gx, gy, gz)
    
def orient_disc_with_manteo(polydata, azimuth, dip, radius=200):
    """ Orients a disc polydata according to dip and azimuth  """
    dip_dir = azimuth % 360
    
    # Plane normal
    normal = compute_plane_normal(dip_dir, dip)

    # Rotate the base disc (normal global = antes (0,0,1)) 
    tf = _transform_from_normals((0,0,1), normal)
    oriented_disc = apply_transform(polydata, tf)
    
    # Local exes
    e1, e2, e3 = compute_local_axes(dip_dir, dip, normal)
    
    # Endpoints
    (s0, s1), (d0, d1) = compute_line_endpoints(radius)

    # Convert to global
    dipdir_pd = build_line(local_to_global(e1, e2, e3, s0), local_to_global(e1, e2, e3, s1))
    dip_pd    = build_line(local_to_global(e1, e2, e3, d0), local_to_global(e1, e2, e3, d1))
    return oriented_disc, dipdir_pd, dip_pd

##################################################################
# --------------------TRANSFORM GEOMETRY------------------------ #
##################################################################
def translate(polydata, x, y, z):
    """ Returns a translated copy of the given polydata"""
    T = vtk.vtkTransform()
    T.Translate(x, y, z)
    return apply_transform(polydata, T)

def create_transformed_geometry(base_disc, x, y, z, azimuth, dip):
    """Moves a disc and its azimuth and dip lines based on coordinates"""
    oriented_disc, oriented_azimuth, oriented_dip = orient_disc_with_manteo(base_disc, azimuth, dip, radius=200)
    disc_t = translate(oriented_disc, x, y, z)
    azimuth_t = translate(oriented_azimuth, x, y, z)
    dip_t = translate(oriented_dip, x, y, z)
    return disc_t, azimuth_t, dip_t

