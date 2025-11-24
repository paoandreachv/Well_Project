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