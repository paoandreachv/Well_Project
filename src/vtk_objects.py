import vtk, random, numpy as np
import src.detailed_functions as detailed_functions
from vtk.util import numpy_support #type: ignore

def create_points(well_data):
    """ Creates VTK points from well coordinates """
    coords = well_data[["X", "Y", "Z"]].to_numpy(dtype=float)
    
    unique_markers = {name: i for i, name in enumerate(sorted(well_data["MarkerName"].unique()))}
    marker_ids = well_data["MarkerName"].map(unique_markers).to_numpy(dtype=int)
    
    azimuth = well_data["Azimuth"].to_numpy(dtype=float)
    dip = well_data["Dip"].to_numpy(dtype=float)
    
    points = vtk.vtkPoints()
    # Convert a numpy array into a VTK array
    points.SetData(numpy_support.numpy_to_vtk(coords))
    
    marker_fault_array = numpy_support.numpy_to_vtk(marker_ids)
    # Assign a name to the array within VTK
    marker_fault_array.SetName("Marker_fault")
    
    azimiuth_array = numpy_support.numpy_to_vtk(azimuth)
    azimiuth_array.SetName("Azimuth")
    
    dip_array = numpy_support.numpy_to_vtk(dip)
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

# TO TEST

def create_filledpolygon_actor(polydata, unique_markers, radius=100, resolution=40,
                               line_color=(0, 0, 0), line_width=2.0):
    """
    Crea actores de discos orientados según Azimuth y Dip, y actores separados para
    las líneas de rumbo/manteo para que sean siempre visibles.
    Devuelve una lista de actores (dos por marker: disco + líneas).
    """
    n_colors = len(unique_markers)
    color_table = detailed_functions.generate_distinct_colors(n_colors)
    marker_to_points = detailed_functions.group_points_by_marker(polydata, n_colors)
    actors = []

    # Base del disco que se reutiliza
    base_disc = vtk.vtkRegularPolygonSource()
    base_disc.SetCenter(0.0, 0.0, 0.0)
    base_disc.SetRadius(radius)
    base_disc.SetNumberOfSides(resolution)
    base_disc.Update()
    base_disc_output = base_disc.GetOutput()

    for marker_index, points in marker_to_points.items():
        if not points:
            continue

        append_discs = vtk.vtkAppendPolyData()
        append_lines = vtk.vtkAppendPolyData()

        for (x, y, z, azimuth, dip) in points:
            disc_geom, line_az_geom, line_dip_geom = detailed_functions.create_transformed_geometry(base_disc_output, x, y, z, azimuth, dip)
            append_discs.AddInputData(disc_geom)
            append_lines.AddInputData(line_az_geom)
            append_lines.AddInputData(line_dip_geom)

        append_discs.Update()
        append_lines.Update()

        # Actor disco
        disc_color = color_table.GetTableValue(marker_index)
        disc_actor = detailed_functions.create_actor(append_discs.GetOutput(), color=disc_color, line=False)
        actors.append(disc_actor)

        # Actor líneas
        line_actor = detailed_functions.create_actor(append_lines.GetOutput(), color=line_color, line=True, line_width=line_width)
        actors.append(line_actor)

    return actors
    
def create_well_line_actors(well_trajectories):
    """ Create a line connecting the top and bottom points of a well """
    actors = []
    for well in well_trajectories["WELLNAME"].unique():
        subset = well_trajectories[well_trajectories["WELLNAME"] == well]
        if len(subset) < 2:
            continue

        subset = subset.sort_values(by = "Z")
        
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

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        line_actor = vtk.vtkActor()
        line_actor.SetMapper(mapper)
        line_actor.GetProperty().SetColor(0.1, 0.1, 0.1)
        line_actor.GetProperty().SetLineWidth(1)
        actors.append(line_actor)

        top = subset.iloc[0]
        label = vtk.vtkBillboardTextActor3D()
        label.SetInput(str(well))
        label.SetPosition(top["X"], top["Y"], top["Z"])
        label.GetTextProperty().SetColor(0.1, 0.1, 0.1)
        label.GetTextProperty().BoldOn()
        label.GetTextProperty().SetFontSize(14)
        actors.append(label)
        
    return actors        
        
    
