import src.vtk_objects as vtk_objects
import vtk

##################################################################
# -----------------------DISC ACTOR----------------------------- #
##################################################################
def create_actor(polydata, color = None, line = False, line_width = 2.0):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    mapper.ScalarVisibilityOff()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    if color is not None:
        actor.GetProperty().SetColor(color[:3])
    if line:
        actor.GetProperty().SetLineWidth(line_width)
        actor.GetProperty().SetColor(1,1,1)
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().LightingOff()
    else:
        actor.GetProperty().SetOpacity(0.9)
        actor.GetProperty().EdgeVisibilityOff()
    return actor

##################################################################
# -------------------------WELL LINES--------------------------- #
##################################################################

def create_line_actor(polydata):
    """ Build and return a vtkActor for a polyline structure"""
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)

    line_actor = vtk.vtkActor()
    line_actor.SetMapper(mapper)
    line_actor.GetProperty().SetColor(0.1, 0.1, 0.1)
    line_actor.GetProperty().SetLineWidth(1)
    return line_actor

def create_well_label(well_name, top_row):
    """ Create a billboard label at the top of the well """
    label = vtk.vtkBillboardTextActor3D()
    label.SetInput(str(well_name))
    label.SetPosition(top_row["X"], top_row["Y"], top_row["Z"])
    label.GetTextProperty().SetColor(0.1, 0.1, 0.1)
    label.GetTextProperty().BoldOn()
    label.GetTextProperty().SetFontSize(10)
    return label

def create_well_line_actors(well_trajectories):
    """ Create a line connecting the top and bottom points of a well """
    actors = []
    
    for well in well_trajectories["WELLNAME"].unique():
        subset = well_trajectories[well_trajectories["WELLNAME"] == well]
        if len(subset) < 2:
            continue

        subset = subset.sort_values(by = "Z", ascending=False)
        
        polydata = vtk_objects.build_well_polyline(subset)
        line_actor = create_line_actor(polydata)
        label_actor = create_well_label(well, subset.iloc[0])
        actors.append(line_actor)
        actors.append(label_actor)
    return actors        
        
    
