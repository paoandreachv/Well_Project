import vtk

def create_renderer():
    """ Creates and returns a VTK renderer """
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)  # White background
    return renderer

def create_render_window(renderer):
    """ Creates and returns a VTK render window """
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 700)
    return render_window

def create_interactor(render_window):
    """ Creates and returns a VTK render window interactor """
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    
    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)
    
    return interactor

